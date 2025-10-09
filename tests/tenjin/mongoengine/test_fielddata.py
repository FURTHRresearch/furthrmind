import datetime

from bson import ObjectId
from tests.conftest import app
import json
from tenjin.database.db import get_db
from tenjin.mongo_engine.Unit import Unit
from tenjin.mongo_engine.Field import Field
from tenjin.mongo_engine.FieldData import FieldData
from tenjin.mongo_engine.Experiment import Experiment

from tenjin.execution.update import Update
from tenjin.execution.append import Append
from tenjin.execution.delete import Delete
from tenjin.execution.pop import Pop

from tenjin.mongo_engine import Database
from tenjin.execution.create import Create


def test_create_fielddata(app):

    field_id = ObjectId("6319f76401c844a436e0b270") # Field ID of "Druck Kammer"
    fielddata_param = {"FieldID": field_id}
    
    Database.set_no_access_check(True)
    field_data_id = Create.create("FieldData", fielddata_param)
    field = Field.objects(id=field_id).first()
    fielddata = FieldData.objects(id=field_data_id).first()
    Database.set_no_access_check(False)
    
    assert fielddata.FieldID.id == field.id
    assert fielddata.Type == field.Type
    assert fielddata.ProjectID.id == field.ProjectID.id
    return fielddata 

def test_append_fielddata_and_update_value(app):
    # FieldData for field "Druck Kammer, which is numeric"
    fielddata = test_create_fielddata(app)
    
    Database.set_no_access_check(True)

    # Exp: 3M - 9501V+_LH326_P_Maskentest
    exp_id = ObjectId("6319f80801c844a436e175ee")
    Append.append("Experiment", "FieldDataIDList", exp_id, fielddata.id)
    exp: Experiment = Experiment.objects(id=exp_id).first()
    field_data_id_list = [fd.id for fd in exp.FieldDataIDList]
    embedded_fielddata_id_list = [fd._id for fd in exp.FieldData]
    assert fielddata.id in field_data_id_list
    assert fielddata.id in embedded_fielddata_id_list
    
    fielddata = FieldData.objects(id=fielddata.id).first()
    assert fielddata.ParentCollection == "Experiment"
    assert fielddata.ParentDataID == exp_id
    
    new_value = 5
    Update.update("FieldData", "Value", new_value, fielddata.id)
    exp: Experiment = Experiment.objects(id=exp_id).first()
    for fd in exp.FieldData:
        if fd._id == fielddata.id:
            assert fd.Value == new_value
    
    unit = Unit.objects(ShortName="cm").first()
    Update.update("FieldData", "UnitID", unit.id, fielddata.id)
    fielddata: FieldData = FieldData.objects(id=fielddata.id).first()
    
    assert fielddata.SIValue == new_value / 100
    
    exp: Experiment = Experiment.objects(id=exp_id).first()
    for fd in exp.FieldData:
        if fd._id == fielddata.id:
            assert fd.SIValue == new_value / 100
    
    Database.set_no_access_check(False)
    
    return fielddata.id, exp_id
    
def test_remove_fielddata(app):
    # FieldData for field "Druck Kammer, which is numeric"
    fielddata_id, exp_id = test_append_fielddata_and_update_value(app)
    
    Database.set_no_access_check(True)
    
    Pop.pop("Experiment", "FieldDataIDList", exp_id, fielddata_id)
    
    exp: Experiment = Experiment.objects(id=exp_id).first()
    fielddata: FieldData = FieldData.objects(id=fielddata_id).first()
    fd_list = [fd.id for fd in exp.FieldDataIDList]
    fd_list_embedded = [fd._id for fd in exp.FieldData]
    assert fielddata_id not in fd_list
    assert fielddata_id not in fd_list_embedded
    assert fielddata is None
    
    fielddata_id, exp_id = test_append_fielddata_and_update_value(app)
    # Resets access check to false => manual set to True again
    Database.set_no_access_check(True)
    fielddata = FieldData.objects(id=fielddata_id).first()
    Delete.delete("FieldData", fielddata_id, include_attributes=["ParentCollection", "ParentDataID"])
    fielddata: FieldData = FieldData.objects(id=fielddata_id).first()
    exp: Experiment = Experiment.objects(id=exp_id).first()
    
    assert fielddata == None
    
    fd_list = [fd.id for fd in exp.FieldDataIDList]
    fd_list_embedded = [fd._id for fd in exp.FieldData]
    assert fielddata_id not in fd_list
    assert fielddata_id not in fd_list_embedded
    
    Database.set_no_access_check(False)
    
    
def test_update_fielddata_id_list(app):
    # FieldData for field "Druck Kammer, which is numeric"
    fielddata = test_create_fielddata(app)
    
    Database.set_no_access_check(True)

    # Exp: 3M - 9501V+_LH326_P_Maskentest
    exp_id = ObjectId("6319f80801c844a436e175ee")
    exp: Experiment = Experiment.objects(id=exp_id).first()
    
    fielddata_id_list = [fd.id for fd in exp.FieldDataIDList]
    
    fielddata_id_list_to_be_deleted = fielddata_id_list[-2:]
    fielddata_id_list = fielddata_id_list[:-2]
    
    Update.update("Experiment", "FieldDataIDList", fielddata_id_list, exp_id)
    
    exp: Experiment = Experiment.objects(id=exp_id).first()
    fd_list = [fd.id for fd in exp.FieldDataIDList]
    fd_list_embedded = [fd._id for fd in exp.FieldData]
    assert fd_list == fielddata_id_list
    assert fd_list_embedded == fielddata_id_list
    
    for fd_id in fielddata_id_list_to_be_deleted:
        assert FieldData.objects(id=fd_id).first() is None
    
    Database.set_no_access_check(False)

    