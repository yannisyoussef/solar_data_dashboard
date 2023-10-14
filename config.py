import os


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///solar_data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SOLAR_DATA_URL = 'http://127.0.0.1:5000/solar_data'


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # You can add more production-specific configurations here.
    # For example, you might want to switch to a different database in production.


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_solar_data.db'
