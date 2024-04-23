
'''
    Log utility which is used for app logs
'''

import logging
import sys

_formatter = logging.Formatter(
    '%(asctime)s:%(name)s: %(levelname)s: %(message)s', '%m/%d/%Y %H:%M:%S')
LOG_PATH = 'logs/'


class Logger:
    '''Logger clas is almost similar to loggin module with customization
       having multiple error handlers
    '''

    def __init__(self, name='root', level=logging.DEBUG, formatter=_formatter):
        self.name = name
        self.level = level

        # Log Handlers
        # Console Handlers
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        # File Handlers
        file_handler = logging.FileHandler(f'{LOG_PATH}all.log', mode='a')
        file_handler.setFormatter(formatter)

        # Complete logging config.
        self.logger = logging.getLogger(name)
        self.logger.propagate = False
        self.logger.setLevel(self.level)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def info(self, *values, extra=None):
        values = ' '.join(str(v) for v in values)
        self.logger.info(values, extra=extra)

    def debug(self, *values, extra=None):
        values = ' '.join(str(v) for v in values)
        self.logger.debug(values)

    def warn(self, *values, extra=None):
        values = ' '.join(str(v) for v in values)
        self.logger.warn(values, extra=extra)

    def error(self, *values, extra=None):
        values = ' '.join(str(v) for v in values)
        self.logger.error(values, extra=extra)

    def critical(self, *values, send_email=True, extra=None):
        values = ' '.join(str(v) for v in values)
        self.logger.critical(values, extra=extra)
        if send_email:
            pass

    def exception(self, exception, extra=None):
        self.logger.exception(exception, extra=extra)