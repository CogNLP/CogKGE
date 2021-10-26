import logging.config

standard_format = '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]' \
                  '[%(levelname)s][%(message)s]'
simple_format = '[%(asctime)s] - [%(name)s] - [%(levelname)s] - [%(message)s]'
LOGGING_DIC = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': standard_format
        },
        'simple': {
            'format': simple_format
        },
    },
    'filters': {},
    'handlers': {

        'stream': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },

        'file': {

            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': None,
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'encoding': 'utf-8',
        },
    },

    'loggers': {
        '': {
            'handlers': ['stream', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


def save_logger():
    logfile_path = "../cogktr_log.log"
    LOGGING_DIC['handlers']['file']['filename'] = logfile_path
    logging.config.dictConfig(LOGGING_DIC)
    logger = logging.getLogger(__name__)
    return logger


logger = save_logger()