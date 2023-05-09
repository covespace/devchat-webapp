"""
conftest.py contains global configurations that are available to all tests.
"""
import os


def pytest_configure(config):  # pylint: disable=unused-argument
    # Set the environment variable to use an in-memory SQLite database
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
