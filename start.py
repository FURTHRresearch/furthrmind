import tenjin
import sys
import subprocess


import app as _app
app = _app.app
# tenjin.create_app(app=app)

from tenjin.database.db import execute_db_migrate
from tenjin.database.database_client import DatabaseClient
from tenjin.file.s3 import execute_cors_method

db = DatabaseClient(app.config["MONGODB_URI"],
                        app.config["MONGODB_DB"])
with app.app_context():
    execute_db_migrate(db, app.config["SERVER_VERSION"], app.config["MONGODB_URI"])

with app.app_context():
    execute_cors_method()

python_interpreter = sys.executable
subprocess.Popen([python_interpreter, "start_worker.py"])
app.run()

