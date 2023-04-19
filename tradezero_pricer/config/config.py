import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    DEFAULT_TICKER_LIST = ['AMZN', 'GOOGL', 'IBM', 'MSFT','NFLX', 'NVDA' 'SPCE', 'TSLA']
    TZP_DB_NAME = os.environ.get('TZP_DB_NAME') or 'tradezero-pricer'
    TZP_ADMIN = os.environ.get('TZP_ADMIN') or 'tradezero'
    TZP_DB_USERNAME = os.environ.get('TZP_DB_USERNAME') or 'tradezero'
    TZP_DB_PASSWORD = os.environ.get('TZP_DB_PASSWORD') or 'verysecret'
    TZP_DB_HOST = os.environ.get('TZP_DB_HOST') or 'localhost'
    TZP_DB_PORT = os.environ.get('TZP_DB_PORT') or 27017
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
    #SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    #MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    #MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    #MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
    #    ['true', 'on', '1']
    #MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    #MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    #MAIL_SUBJECT_PREFIX = '[TradeZero Pricer]'
    #MAIL_SENDER = 'TradeZero Pricer <tradezero-pricer@example.com>'

    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('TZP_CONN_STRING') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    @classmethod
    def init_app(this, app):
        Config.init_app(app)

        import logging
        # from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        #if getattr(this, 'MAIL_USERNAME', None) is not None:
        #    credentials = (this.MAIL_USERNAME, this.MAIL_PASSWORD)
        #    if getattr(this, 'MAIL_USE_TLS', None):
        #        secure = ()
        #mail_handler = SMTPHandler(
        #    mailhost=(this.MAIL_SERVER, this.MAIL_PORT),
        #    fromaddr=this.MAIL_SENDER,
        #    toaddrs=[this.TZP_ADMIN],
        #    subject=this.MAIL_SUBJECT_PREFIX + ' Application Error',
        #    credentials=credentials,
        #     secure=secure)
        # mail_handler.setLevel(logging.ERROR)
        # app.logger.addHandler(mail_handler)


class HerokuConfig(ProductionConfig):
    SSL_REDIRECT = True if os.environ.get('DYNO') else False

    @classmethod
    def init_app(this, app):
        ProductionConfig.init_app(app)

        # handle reverse proxy server headers
        try:
            from werkzeug.middleware.proxy_fix import ProxyFix
        except ImportError:
            from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


class ContainerConfig(ProductionConfig):
    DEBUG = True
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
        app.logger.addHandler(syslog_handler)


config = {
    'container': ContainerConfig,
#    'unix': UnixConfig,
#    'production': ProductionConfig,
#    'default': ProductionConfig
}
