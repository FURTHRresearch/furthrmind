from tenjin.database.database_client import DatabaseClient
from tenjin.database.database_version_update import DatabaseVersionUpdate

import click
from flask import current_app
from flask.cli import with_appcontext

from pymongo import AsyncMongoClient

import os

from tenjin.execution.create import Create
from DemoDB import restore_database

""" Utility methods to take care of the database access and migration.
Provides a method to access the global database client instance and 
a method to close the connection. The migration method should be executed
after every server restart and takes care of all version related changes
in the database layout. The layout check method should be executed as well
since it guarantees all database entries to be coherent. """

class DBStorage:
    db = None


def get_db(force=False):
    if DBStorage.db is None or force:
        DBStorage.db = DatabaseClient(current_app.config["MONGODB_URI"],
                                      current_app.config["MONGODB_DB"])

    return DBStorage.db

def get_db_async():
    
    client = AsyncMongoClient(current_app.config["MONGODB_URI"])
    db = client[current_app.config["MONGODB_DB"]]
    return db
    

def close_db(e=None):
    if DBStorage.db is None:
        return
    DBStorage.db.mongoClient.close()
    DBStorage.db = None

def execute_db_migrate(db, softwareVersion, uri):
    from tenjin.mongo_engine import Database
    last_version = Database.check_for_existing_version()
    if not last_version:
        #db not found, restore demo db
        restore_database(uri)

    last_version = Database.check_for_existing_version()

    # softwareVersion = current_app.config["SERVER_VERSION"]

    if last_version != softwareVersion:
        print("Database version : " + last_version + " detected!")
        print("SoftwareVersion : " + softwareVersion)
        print("Corresponding Updates are performed!")
        updater = DatabaseVersionUpdate(db, last_version, softwareVersion)
        updater.performDBUpdate()


@click.command('db-migrate')
@with_appcontext
def db_migrate():
    db = DatabaseClient(current_app.config["MONGODB_URI"], current_app.config["MONGODB_DB"],
                        )
    execute_db_migrate(db, current_app.config["SERVER_VERSION"],
                       current_app.config["MONGODB_URI"])


def execute_create_admin(db, email=''):
    if email == '':
        return
    email = email.lower()
    password = "db" + os.urandom(16).hex()
    # pwhash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    doc = {
        "Email": email,
        "Admin": True,
        "Password": password
    }

    Create.create("User", doc, db, None)

    print('User created. Check your inbox.')

def init_app(app):
    # Don't close db connection when context (request) ends. This will slow donw the application
    # app.teardown_appcontext(close_db)
    app.cli.add_command(db_migrate)

