import os

DEBUG = True

SPLUNK_HOST = 'splunk.example.com'
SPLUNK_PORT = '8089'
SPLUNK_USERNAME = 'changeme'
SPLUNK_PASSWORD = 'changeme'
SPLUNK_INDEX = 'main'
SPLUNK_HOSTNAME = "link-consus.mailbeaker.dev"
SPLUNK_VERIFY = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(created)f %(exc_info)s %(filename)s %(funcName)s %(levelname)s %(levelno)s %(lineno)d %(module)s %(message)s %(pathname)s %(process)s %(processName)s %(relativeCreated)d %(thread)s %(threadName)s'
        }
    },
    'handlers': {
        'splunk': {
            'level': 'INFO',
            'class': 'splunk_handler.SplunkHandler',
            'formatter': 'json',
            'host': SPLUNK_HOST,
            'port': SPLUNK_PORT,
            'username': SPLUNK_USERNAME,
            'password': SPLUNK_PASSWORD,
            'index': SPLUNK_INDEX,
            'hostname': SPLUNK_HOSTNAME,
            'sourcetype': 'json',
            'verify': SPLUNK_VERIFY
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'splunk'],
            'level': 'INFO'
        }
    }
}
