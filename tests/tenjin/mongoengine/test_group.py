import datetime

from bson import ObjectId
from tests.conftest import app
import json
from tenjin.database.db import get_db
from tenjin.mongo_engine.Unit import Unit
from tenjin.execution.update import Update
from tenjin.mongo_engine import Database
import random
import string
from tenjin.execution.create import Create

def test_create_group(app):
    
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    param = {
        "Name": name,
        "ProjectID": ObjectId("6319f6fb01c844a436e07971"),
    }
    
    Database.set_no_access_check(True)
    group_id = Create.create("Group", param)
    Database.set_no_access_check(False)
    
    assert isinstance(group_id, ObjectId)
    return group_id
    