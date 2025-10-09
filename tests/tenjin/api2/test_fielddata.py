import datetime

from bson import ObjectId
from tests.conftest import app, client_api2
import json
from tenjin.database.db import get_db
from urllib import parse

project_id = '6319f6fb01c844a436e07971'

def test_get_fielddata(client_api2):
    project_id = '6319f6fb01c844a436e07971'
    field_name = "Test Field"
    field_type = "Text"
    
    # create a new fielddata
    data = {
        "fieldname": field_name,
        "fieldtype": field_type,
        "value": "Test Value",
    }
    
    r = client_api2.post(f"/api2/project/{project_id}/fielddata", json=data)
    assert r.status_code == 200
    data = r.json
    fielddata_id = data["results"][0]
    
    r = client_api2.get(f"/api2/project/{project_id}/fielddata/{fielddata_id}")
    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    result = data["results"][0]
    assert result["fieldname"] == field_name
    assert result["fieldtype"] == "SingleLine"
    assert result["value"] == "Test Value"

def test_post_and_delete_fielddata(client_api2):
    
    """ calling this method will create the app fixture which resets the test_db. """
    field_name = "Test Field"
    field_type = "Text"
    
    # create a new fielddata text field
    data = {
        "fieldname": field_name,
        "fieldtype": field_type,
        "value": "Test Value",
    }
    
    r = client_api2.post(f"/api2/project/{project_id}/fielddata", json=data)
    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    fielddata_id = data["results"][0]
    
    # test updating the fielddata by id
    data = {
        "id": fielddata_id,
        "value": "Test Value",
    }
    
    r = client_api2.post(f"/api2/project/{project_id}/fielddata", json=data)
    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    fielddata_id = data["results"][0]
    
    # deleting fielddata by id
    r = client_api2.delete(f"/api2/project/{project_id}/fielddata/{fielddata_id}")
    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    assert data["results"][0] == fielddata_id


def get_fd(client_api2, fielddata_id):
        r = client_api2.get(f"/api2/project/{project_id}/fielddata/{fielddata_id}")
        assert r.status_code == 200
        data = r.json
        assert "status" in data
        assert data["status"] == "ok"
        assert "results" in data
        assert isinstance(data["results"], list)
        result = data["results"][0]
        return result

def test_post_fielddata_date(client_api2):
    import pytz
    tz = pytz.timezone("Europe/Berlin")
    date = datetime.datetime(2023, 1, 1, 0, 0, 0)
    date = tz.localize(date)
    
    date_iso = date.isoformat()
    date_unix = date.timestamp()
    
    new_date = datetime.datetime.fromisoformat(date_iso)
    new_date = new_date.astimezone(tz=datetime.timezone.utc)
    new_date_unix = new_date.timestamp()
    assert date_unix == new_date_unix

    new_date = datetime.datetime.fromtimestamp(date_unix)
    new_date_unix = new_date.timestamp()
    assert date_unix == new_date_unix

    data = {
        "fieldname": "Test Date Field",
        "fieldtype": "Date",
        "value": date.isoformat()
    }
    

    r = client_api2.post(f"/api2/project/{project_id}/fielddata", json=data)
    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    fielddata_id = data["results"][0]

    # test getting the fielddata by id
    result = get_fd(client_api2, fielddata_id)
    assert result["fieldname"] == "Test Date Field"
    assert result["fieldtype"] == "Date"
    
    assert result["value"] == date.timestamp()
    
    date_from_result = datetime.datetime.fromtimestamp(result["value"], 
                                                       tz=tz)
    assert date_from_result == date

    # update by timestamp
    data = {
        "id": fielddata_id,
        "value": date.timestamp()
    }
    r = client_api2.post(f"/api2/project/{project_id}/fielddata", json=data)
    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    fielddata_id = data["results"][0]

    # test getting the fielddata by id
    result = get_fd(client_api2, fielddata_id)
    assert result["fieldname"] == "Test Date Field"
    assert result["fieldtype"] == "Date"
    
    assert result["value"] == date.timestamp()


def test_post_fielddata_numeric(client_api2):
    

    # test creating a new fielddata numeric with unit
    data = {
        "fieldname": "Test Numeric Field",
        "fieldtype": "Numeric",
        "value": 123.45,
        "unit": {
            "name": "cm",
        }
    }
    
    r = client_api2.post(f"/api2/project/{project_id}/fielddata", json=data)
    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    fielddata_id = data["results"][0]
    
    # test getting the fielddata by id
    result = get_fd(client_api2, fielddata_id)
    assert result["fieldname"] == "Test Numeric Field"
    assert result["fieldtype"] == "Numeric"
    assert result["value"] == 123.45
    assert result["unit"]["name"] == "cm"
    
    
def test_post_fielddata_combobox(client_api2):
    # test creating a new fielddata with combobox field type
    data = {
        "fieldname": "Test Combobox Field",
        "fieldtype": "ComboBox",
        "value": "Option 1"
    }
    
    r = client_api2.post(f"/api2/project/{project_id}/fielddata", json=data)
    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    fielddata_id = data["results"][0]
    
    # test getting the fielddata by id
    result = get_fd(client_api2, fielddata_id)
    assert result["fieldname"] == "Test Combobox Field"
    assert result["fieldtype"] == "ComboBox"
    assert isinstance(result["value"], dict)
    assert "name" in result["value"]
    assert result["value"]["name"] == "Option 1"
    assert "id" in result["value"]
    combo_id = result["value"]["id"]
    
    # test update the combobox fielddata to None
    data = {
        "id": fielddata_id,
        "value": None,
    }

    r = client_api2.post(f"/api2/project/{project_id}/fielddata", json=data)
    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    fielddata_id = data["results"][0]
    
    # test getting the fielddata by id
    result = get_fd(client_api2, fielddata_id)
    assert result["fieldname"] == "Test Combobox Field"
    assert result["fieldtype"] == "ComboBox"
    assert result["value"] is None
    
    # test update combo by id
    data = {
        "id": fielddata_id,
        "value": {
            "id": combo_id
        }   
    }
    
    r = client_api2.post(f"/api2/project/{project_id}/fielddata", json=data)
    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    fielddata_id = data["results"][0]
    
    # test getting the fielddata by id
    result = get_fd(client_api2, fielddata_id)
    assert result["fieldname"] == "Test Combobox Field"
    assert result["fieldtype"] == "ComboBox"
    assert "name" in result["value"]
    assert result["value"]["name"] == "Option 1"
    assert "id" in result["value"]
    assert result["value"]["id"] == combo_id
    
def test_post_fielddata_notebook(client_api2):
    data = {
        "fieldname": "Test Notebook Field",
        "fieldtype": "MultiLine",
        "value": "This is a test notebook entry.",
    }
    
    r = client_api2.post(f"/api2/project/{project_id}/fielddata", json=data)
    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    fielddata_id = data["results"][0]
    
    # test getting the fielddata by id
    result = get_fd(client_api2, fielddata_id)
    assert result["fieldname"] == "Test Notebook Field"
    assert result["fieldtype"] == "MultiLine"
    assert isinstance(result["value"], dict)
    assert result["value"]["content"] == "This is a test notebook entry."
    
    # update Notebook check if a second notebook is created or the existing one is updated. 
    # to check this, the database must be checked manually, e.g. in the versioning table
    
    data = {
        "id": fielddata_id,
        "value": "Updated Notebook",
    }
    r = client_api2.post(f"/api2/project/{project_id}/fielddata", json=data)
    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    fielddata_id = data["results"][0]
    
    result = get_fd(client_api2, fielddata_id)
    assert result["fieldname"] == "Test Notebook Field"
    assert result["fieldtype"] == "MultiLine"
    assert isinstance(result["value"], dict)
    assert result["value"]["content"] == "Updated Notebook"