import os
from inspect import isclass
from typing import Annotated, get_origin
from urllib.parse import urlparse, urlunparse
from uuid import uuid4

import asyncpg
import httpx
import pytest
import pytest_asyncio
from attr import dataclass
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from pytest_asyncio import is_async_test

from src import AppConfig, create_app, database
from src.database.repository import Repository
from src.database.service import Connection
from src.test_common import HTMLClient
from src.utils import Injector

load_dotenv(".env.development")
pytest_plugins = ["pytest_asyncio"]


MAILPIT_URL = os.environ["MAILPIT_URL"]


def pytest_collection_modifyitems(items):
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


@pytest.fixture(scope="session", autouse=True)
def clear_mailpit(request):

    def finalizer():
        httpx.delete(f"{MAILPIT_URL}/messages")

    httpx.delete(f"{MAILPIT_URL}/messages")

    request.addfinalizer(finalizer)


@pytest_asyncio.fixture(loop_scope="session", scope="session", autouse=False)
async def test_database_url(request):
    name = f"test_{uuid4()}"
    cnn = await asyncpg.connect(os.environ["DATABASE_URL"])
    await cnn.execute(f'create database "{name}" with template test')
    await asyncpg.create_pool(os.environ["DATABASE_URL"])

    url = urlparse(os.environ["DATABASE_URL"])
    url = url._replace(path=name)

    yield urlunparse(url)

    await cnn.execute(f'drop database "{name}"')


@pytest_asyncio.fixture(loop_scope="session")
async def cnn(test_database_url):
    cnn = await asyncpg.connect(test_database_url)
    yield Connection(cnn=cnn)
    await cnn.close()


@pytest.fixture(scope="function")
def app(test_database_url):
    return create_app(AppConfig(DATABASE_URL=test_database_url))


@pytest.fixture(scope="function")
def client(app):
    with TestClient(app) as client:
        print(app, client)
        yield HTMLClient(client=client)


@pytest.fixture(scope="function")
def injector(cnn):
    return Injector(overrides={Connection: cnn})
