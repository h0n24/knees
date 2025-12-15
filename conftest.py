import os

import django
import pytest
from django.test import Client
from django.test.runner import DiscoverRunner
from django.test.utils import setup_test_environment, teardown_test_environment

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apps.backend.config.settings")
django.setup()


@pytest.fixture(scope="session", autouse=True)
def django_test_environment():
    setup_test_environment()
    test_runner = DiscoverRunner()
    old_config = test_runner.setup_databases()
    yield
    test_runner.teardown_databases(old_config)
    teardown_test_environment()


@pytest.fixture()
def client():
    return Client()
