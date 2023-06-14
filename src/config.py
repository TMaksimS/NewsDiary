import os

from dotenv import load_dotenv

load_dotenv()

"""Postgres DataBase"""
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

"""JWT secret key"""
SECRET_KEY = os.environ.get("SECRET_KEY_TOKEN")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("EXPIRE")

"""Redis DataBase"""
R_HOST = os.environ.get("REDIS_HOST")
R_PORT = os.environ.get("REDIS_PORT")