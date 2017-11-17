from celery import Celery
import os
import time
from celery_request import Request
from celery.utils.log import get_task_logger
import json


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
        '/tmp/ogc/inputs': '/inputs',
        '/tmp/ogc/data': '/data'
    }
    if not request.volume_mapping:
        request.volume_mapping = volume_mapping

    request.body['input_data']['task_id'] = task_id

    #Start processing
    request.set_progress(0)
    error_code = run_image(request)
    if error_code != 0:
        raise Exception("Error in running container")
    request.set_progress(50)
    time.sleep(20)  # Fake progression
    request.set_progress(100)

    json_output_file = '/tmp/ogc/tasks/{uuid}/outputs/{uuid}.json'.format(uuid=task_id)
    if os.path.exists(json_output_file):
        json_output = json.load(open(json_output_file))
    else:
        json_output = {'outputs': 'output_from_application'}
    # Get output url
    # output_data_url: http://10.1.35.59/fs/tasks/6b0d3c64-5978-483c-9fc3-f37cdb46c821/outputs/outputs/generate_dem_test/DEM_RS2_OK79000_PK698379_DK627315_FQ9W_20160907_013546_HH_VV_HV_VH_SLC_worker2.tif
    # output_data_WMS_url: http://132.217.140.40:8080/geoserver/OGC01/wms?service=WMS&version=1.1.0&request=GetMap&layers=OGC01:RS2_OK79000_PK698379_DK627315_FQ9W_20160907_013546_HH_VV_HV_VH_SLC-2017-08-02T20:30:46.818016Z&styles=&bbox=-118.93031183853228,49.834373782054,-118.15157741042583,50.228387801408914&width=768&height=388&srs=EPSG:4326&format=image%2Fpng&bgcolor=000000

    return {'result': json_output}




