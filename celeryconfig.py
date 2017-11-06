# -*- coding: utf-8 -*-
"""
Configuration values for worker processes.
"""
import os

BROKER_HOST = os.getenv('AMQP_HOST','localhost')
BROKER_ADMIN_PORT = '15672'
BROKER_ADMIN_UNAME = os.getenv('AMQP_USERNAME','test')
BROKER_ADMIN_PASS = os.getenv('AMQP_PASSWORD','asdf')
BROKER_PORT = os.getenv('AMQP_PORT','5672')
# Broker settings ------------------------------------------------------------
BROKER_URL = "amqp://"+BROKER_ADMIN_UNAME+":"+BROKER_ADMIN_PASS+"@"+BROKER_HOST+":"+BROKER_PORT+"//"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Result backend settings ----------------------------------------------------
CELERY_RESULT_BACKEND = "amqp"
CELERY_RESULT_SERIALIZER = 'json'

# Worker settings ------------------------------------------------------------
CELERYD_PREFETCH_MULTIPLIER = 1

# Logging settings -----------------------------------------------------------
CELERYD_TASK_LOG_FORMAT = ("[%(asctime)s: %(levelname)s/%(processName)s] "
                           "[%(task_name)s(%(task_id)s)] - %(name)s - "
                           "%(message)s")

CELERYD_LOG_FORMAT = ("[%(asctime)s: %(levelname)s/%(processName)s] "
                      "- %(name)s - %(message)s")