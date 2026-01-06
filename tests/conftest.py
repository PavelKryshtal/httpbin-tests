import logging
import os

import pytest
import requests
from dotenv import load_dotenv


class TestConfig:
    def __init__(self):
        load_dotenv()
        self.base_url = os.getenv("BASE_URL")


@pytest.fixture(scope="session")
def config() -> TestConfig:
    return TestConfig()


@pytest.fixture(scope="session")
def client():
    session = requests.Session()
    yield session
    session.close()


def pytest_configure():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
