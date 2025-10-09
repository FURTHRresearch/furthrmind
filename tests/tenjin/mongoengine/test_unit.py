import datetime

from bson import ObjectId
from tests.conftest import app
import json
from tenjin.database.db import get_db
from tenjin.mongo_engine.Unit import Unit
from tenjin.execution.update import Update
from tenjin.mongo_engine import Database


def test_update_definition(app):
    unit = Unit.objects(ShortName="g/cm^3").first()
    Database.set_no_access_check(True)
    Update.update("Unit", "Definition", "g/cm/cm/cm", unit.id)
    Database.set_no_access_check(False)
    unit = Unit.objects(ShortName="g/cm^3").first()
    assert "<u>" in unit.Definition
    print(unit)
    