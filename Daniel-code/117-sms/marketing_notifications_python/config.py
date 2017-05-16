class DefaultConfig(object):
    SECRET_KEY = '%^!@@*!&$8xdfdirunb52438#(&^874@#^&*($@*(@&^@)(&*)Y_)((+'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/default.db'
    TWILIO_ACCOUNT_SID = 'AC7809247efc049679c727713e5f345aaa'
    TWILIO_AUTH_TOKEN = '8f4360c99898b2c9202ab5957b6fd00c'
    TWILIO_NUMBER = '+19492429784'


class DevelopmentConfig(DefaultConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/develconfig.db'


class TestConfig(DefaultConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/testconfig.db'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False


config_env_files = {
    'test': 'marketing_notifications_python.config.TestConfig',
    'development': 'marketing_notifications_python.config.DevelopmentConfig',
}
