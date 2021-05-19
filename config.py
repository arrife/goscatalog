import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    CONNECTION = {
        'host':'127.0.0.1',
        'port': 3306,
        'user':'root',
        'password':'uSy5Nkf4Wnr4ptYekPsa37QCGMhZrwCv',
        'database':'govcatalog'
    }
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my first app'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        "mariadb+pymysql://{user}:{password}@{host}:{port}/{database}".format(**CONNECTION)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')