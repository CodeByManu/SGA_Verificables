import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'miy_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://sga_user:sga_user@localhost/sga_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False