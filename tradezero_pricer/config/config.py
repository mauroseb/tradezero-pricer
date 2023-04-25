import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    DEFAULT_TICKER_LIST = ['AMZN', 'GOOGL', 'IBM', 'MSFT','NFLX', 'NVDA' 'SPCE', 'TSLA']
    TZP_DB_NAME = os.environ.get('TZP_DB_NAME') or 'tradezero-pricer'
    TZP_ADMIN = os.environ.get('TZP_ADMIN') or 'tradezero'
    TZP_DB_USERNAME = os.environ.get('TZP_DB_USERNAME') or 'tradezero'
    TZP_DB_PASSWORD = os.environ.get('TZP_DB_PASSWORD')
    TZP_DB_HOST = os.environ.get('TZP_DB_HOST') or 'localhost'
    TZP_DB_PORT = os.environ.get('TZP_DB_PORT') or 27017
    TZP_VERSION = os.environ.get('TZP_VERSION')
    TZP_VERSION_COMMIT = os.environ.get('TZP_COMMIT')
    TZP_SLOW_DB_QUERY_TIME = 0.5
    SSL_REDIRECT = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    MONGODB_SETTINGS = {
        'host': TZP_DB_HOST,
        'port': TZP_DB_PORT,
        'db': TZP_DB_NAME,
        'username': TZP_DB_USERNAME,
        'password': TZP_DB_PASSWORD
        }

    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):

    @classmethod
    def init_app(this, app):
        Config.init_app(app)


class ContainerConfig(ProductionConfig):
    #DEBUG = True
    PROPAGATE_EXCEPTIONS = True
    TESTING = True
    @classmethod
    def init_app(this, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(filename)s: %(lineno)d]')
        file_handler.setFormatter(file_formatter)
        app.logger.addHandler(file_handler)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(this, app):
        ProductionConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(filename)s: %(lineno)d]')
        syslog_handler.setFormatter(file_formatter)
        app.logger.addHandler(syslog_handler)


config = {
    'container': ContainerConfig,
    'unix': UnixConfig,
    'production': ProductionConfig,
    'default': ContainerConfig,
}
