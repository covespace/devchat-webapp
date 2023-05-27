import os
import subprocess
import time
from multiprocessing import Process
import pytest
import uvicorn
from webapp.main import app
from webapp.controller import get_users_of_organization
from webapp.controller import get_organization_id_by_name

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.environ['API_BASE_URL'] = "http://localhost:8000"


@pytest.fixture(scope='module', name='file1_path')
def fixture_file1_path():
    return os.path.join(TEST_DATA_DIR, 'file1.xlsx')


@pytest.fixture(scope='module', name='file2_path')
def fixture_file2_path():
    return os.path.join(TEST_DATA_DIR, 'file2.xlsx')


def run_app():
    uvicorn.run(app, host="0.0.0.0", port=8000)


@pytest.fixture(scope="module", name="local_app")
def fixture_local_app():
    server = Process(target=run_app)
    server.start()
    time.sleep(1)
    yield
    server.terminate()


def test_process_file1(database, file1_path, local_app):  # pylint: disable=W0613
    result = subprocess.run(["python", "scripts/upload_create.py", file1_path],
                            stdout=subprocess.PIPE, text=True, check=True)
    print(result.stdout)

    org_id = get_organization_id_by_name(database, 'covespace')
    assert org_id is not None
    users = get_users_of_organization(database, org_id)
    assert len(users) == 4


def test_process_file2(database, file1_path, file2_path, local_app):  # pylint: disable=W0613
    result = subprocess.run(["python", "scripts/upload_create.py", file1_path],
                            stdout=subprocess.PIPE, text=True, check=True)
    print(result.stdout)
    result = subprocess.run(["python", "scripts/upload_create.py", file2_path],
                            stdout=subprocess.PIPE, text=True, check=True)
    print(result.stdout)

    org1_id = get_organization_id_by_name(database, 'covespace')
    assert org1_id is not None
    assert len(get_users_of_organization(database, org1_id)) == 4

    org2_id = get_organization_id_by_name(database, 'merico')
    assert org2_id is not None
    users = get_users_of_organization(database, org2_id)
    assert len(users) == 4
