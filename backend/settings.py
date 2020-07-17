import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DATABASE_NAME = os.environ.get("DATABASE_NAME")
DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")



TEST_DATABASE_NAME = os.environ.get("TEST_DATABASE_NAME")
TEST_DATABASE_USERNAME = os.environ.get("TEST_DATABASE_USERNAME")
TEST_DATABASE_PASSWORD = os.environ.get("TEST_DATABASE_PASSWORD")



