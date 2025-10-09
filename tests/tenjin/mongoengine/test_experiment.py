import datetime

from bson import ObjectId
from tests.conftest import app
import json
from tenjin.database.db import get_db
from tenjin.mongo_engine.Unit import Unit
from tenjin.execution.update import Update
from tenjin.mongo_engine import Database
from .test_group import test_create_group
import random
import string
from tenjin.execution.create import Create
from tenjin.execution.update import Update
from tenjin.execution.delete import Delete
from tenjin.cache import Cache

def test_create_experiment_update_and_cache(app):
    group_id = test_create_group(app)
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    experiment_param = {
        "Name": name,
        "FieldDataIDList": [],
        "GroupIDList": [group_id],
    }
    Database.set_no_access_check(True)
    experiment_id = Create.create("Experiment", experiment_param)
    
    assert isinstance(experiment_id, ObjectId)
    
    db = get_db().db
    experiment = db.Experiment.find_one({"_id": experiment_id}, {"_id": 1, "GroupIDList": 1})
    assert experiment is not None
    
    cache = Cache.get_cache()
    cache.set(str(experiment_id), experiment, timeout=3600)
    exp_cache = cache.get(str(experiment_id))
    exp_cache["_id"] = experiment["_id"]
    
    new_group = test_create_group(app)
    
    Database.set_no_access_check(True)
    Update.update("Experiment", "GroupIDList", [new_group], experiment_id)
    
    exp_cache = cache.get(str(experiment_id))
    assert exp_cache is None
    
    Database.set_no_access_check(False)
    return experiment_id

def test_link_experiment_and_cache(app):
    group_id = test_create_group(app)
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    experiment_param = {
        "Name": name,
        "GroupIDList": [group_id],
    }
    Database.set_no_access_check(True)
    experiment_id = Create.create("Experiment", experiment_param)
    
    assert isinstance(experiment_id, ObjectId)
    
    
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    experiment_param = {
        "Name": name,
        "GroupIDList": [group_id],
    }
    Database.set_no_access_check(True)
    experiment_id_2 = Create.create("Experiment", experiment_param)
    
    
    db = get_db().db
    experiment = db.Experiment.find({"_id": {"$in": [experiment_id, experiment_id_2]}}, {"_id": 1, "GroupIDList": 1})
    experiments = experiment.to_list()
    for exp in experiments:
        assert exp is not None
    
    link_parameter = {
        "DataID1": experiment_id,
        "Collection1": "Experiment",
        "DataID2": experiment_id_2,
        "Collection2": "Experiment",
    }
    link_id = Create.create("Link", link_parameter)
    
    cache = Cache.get_cache()
    cache.set(f"link_{experiment_id}", [experiment_id_2], timeout=3600)
    
    link_cache = cache.get(f"link_{experiment_id}")
    assert link_cache == [experiment_id_2]
    
    Delete.delete("Link", link_id)
    
    link_cache = cache.get(f"link_{experiment_id}")
    assert link_cache is None
    