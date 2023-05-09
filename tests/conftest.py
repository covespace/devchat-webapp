# conftest.py
import os


def pytest_configure(config):  # pylint: disable=unused-argument
    # Set the environment variable to use an in-memory SQLite database
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
