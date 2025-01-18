import os

PROD_ENV = os.environ["ENV"] == "prod"
DEV_ENV = os.environ["ENV"] == "dev"
TEST_ENV = os.environ["ENV"] == "test"
DATABASE_URL = os.environ["DATABASE_URL"]
LOG_LEVEL = os.environ["LOG_LEVEL"]
