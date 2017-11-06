from celery import Celery
import os
import time
from celery_request import Request
from celery.utils.log import get_task_logger


PROCESS_NAME = 'worker.joblauncher'
CELERY_APP = Celery(PROCESS_NAME)


def get_env_cmd(envar=dict()):
    env_cmd = "".join([" -e WPS_INPUT_{0}={1}".format(key.upper(), val) for key, val in envar.items()])
    return env_cmd

def get_double_dash_cmd(envar=dict()):
    double_dash_cmd = "".join([" --{0} {1}".format(key, val) for key, val in envar.items()])
    return double_dash_cmd

def get_volume_mapping(volume_mapping=dict()):
    volume_mapping_cmd = "".join([" -v {0}:{1}".format(host_dir, container_dir) for host_dir, container_dir in volume_mapping.items()])
    return volume_mapping_cmd

def run_image(req):
    if req.param_as_envar:
        cmd = "docker run --rm {volume} {env_variable} {image}:{version}".format(
            env_variable=get_env_cmd(req.input_data),
            image=req.dockerim_name,
            version=req.dockerim_version,
            volume=get_volume_mapping(req.volume_mapping),
        )
    else:
        cmd = "docker run --rm {volume} {image}:{version} {double_dash_param}".format(
            double_dash_param=get_double_dash_cmd(req.input_data),
            image=req.dockerim_name,
            version=req.dockerim_version,
            volume=get_volume_mapping(req.volume_mapping),
        )

    print "cmd = "+cmd

    retcode = os.system(cmd)
    print("retcode={}".format(retcode))
    return retcode


@CELERY_APP.task(bind=True, name=PROCESS_NAME)
def task_joblauncher(self, args):
    task_id = self.request.id
    logger = get_task_logger(__name__)
    logger.info("Got request to process task # %s", task_id)
    request = Request(args, self)

    volume_mapping = {
        '/tmp/ogc/tasks/{uuid}/outputs'.format(uuid=task_id): '/outputs',
        '/tmp/ogc/tasks/inputs': '/inputs',
        '/tmp/ogc/tasks/data': '/data'
    }
    if not request.volume_mapping:
        request.volume_mapping = volume_mapping

    #Start processing
    request.set_progress(0)
    run_image(request)
    request.set_progress(50)
    time.sleep(20)  # Fake progression
    request.set_progress(100)


    # return something like the progression status? 0, 10, 20 ... 10%
    # which goes back into the celery queue

    return {'result': {'type': 'Useless', 'value': args}}




