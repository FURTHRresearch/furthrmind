import os

import pytest
from werkzeug.test import EnvironBuilder

from tenjin import create_app

os.environ["TESTING"] = "True"

from app import app as test_app


@pytest.fixture(scope="session")
def app():
    init_db = True
    if test_app.config["SKIP_DB_INIT"]:
        init_db = False
        
    if init_db:
        init_database()

    with test_app.app_context():
        create_app(app=test_app)
        yield test_app


def init_database():
    with test_app.app_context():
        from tenjin.database.db import execute_db_migrate
        from tenjin.database.db import DatabaseClient

        if test_app.config["MONGODB_DB"] != "test_db":
            raise ValueError("Wrong db in config")
        if not test_app.config["MONGODB_URI"].endswith("test_db"):
            raise ValueError("Wrong db in config")

        db = DatabaseClient(test_app.config["MONGODB_URI"], test_app.config["MONGODB_DB"],
                            )
        db.db.client.drop_database(test_app.config["MONGODB_DB"])

        execute_db_migrate(db, test_app.config["SERVER_VERSION"],
                           test_app.config["MONGODB_URI"])

@pytest.fixture()
def client(app):
    test_client = app.test_client()
    data = {"email": "admin@furthrmind.com", "password": "admin"}
    r = test_client.post("/web/login", data=data)
    assert r.status_code == 200
    session = r.headers.get("Set-Cookie")
    test_client.environ_base["Cookie"] = session
    return test_client

@pytest.fixture()
def client_api2(app):
    home = os.path.expanduser("~")
    api_key_file = os.path.join(home, "furthrmind_demo_api_key.txt")
    with open(api_key_file, "r") as f:
        api_key = f.read()
    
    test_client = app.test_client()
    builder = EnvironBuilder(headers={"X-API-KEY": api_key})
    test_client.environ_base = builder.get_environ()
    return test_client

@pytest.fixture()
def client_api2_wrong_key(app):
    home = os.path.expanduser("~")
    api_key_file = os.path.join(home, "furthrmind_demo_api_key.txt")
    with open(api_key_file, "r") as f:
        api_key = f.read().strip()
    api_key = api_key + "wrong"
    test_client = app.test_client()
    test_client.environ_base["X-API-KEY"] = api_key
    return test_client


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
