

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI ='mysql+mysqlconnector://root:welcomesql1@localhost/mechanic_shop_db'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache' ## Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT=300  ## 5 mintues once cache could be refresh

class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'  ## which is a lightweight database suitable for testing the creation and manipulation of data.
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'

class ProductionConfig:
    pass
    