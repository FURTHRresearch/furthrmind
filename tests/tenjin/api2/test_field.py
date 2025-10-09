import datetime

from bson import ObjectId
from tests.conftest import app, client_api2
import json
from tenjin.database.db import get_db
from urllib import parse

def test_get_field(client_api2):
    """ calling this method will create the app fixture which resets the test_db. """
    
    # get by field_id of a numeric field
    field_id_numeric = "6319f76301c844a436e0b157"
    
    # get by id via route
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/field/{field_id_numeric}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == field_id_numeric
    assert data["results"][0]["name"] == "Differenzdruck Kammer"
    assert data["results"][0]["type"] == 'Numeric'
    
    # get by field_id of a combobox_field to check the comboboxentries
    
    field_id_combo = "6319f76301c844a436e0b14c"
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/field/{field_id_combo}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == field_id_combo
    assert data["results"][0]["name"] == "Hersteller"
    assert data["results"][0]["type"] == 'ComboBox'
    
    
    # get by name via query string
    field_name = "Differenzdruck Kammer"
    query = []
    query.append(("name", field_name))
    field_name = "Hersteller"
    query.append(("name", field_name))

    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/fields?{url_query}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 2
    names = [r["name"] for r in data["results"]]
    assert "Differenzdruck Kammer" in names
    assert "Hersteller" in names



def test_get_all_field(client_api2):
    """ calling this method will create the app fixture which resets the test_db. """
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/fields")
    assert r.status_code == 200
    data = r.json
    for r in data["results"]:
        assert "id" in r
        assert "name" in r
        assert "type" in r


def test_post_and_delete_field(client_api2):
    """ calling this method will create the app fixture which resets the test_db. """
    data = {
        "name": "Test Field",
        "type": "Numeric",
    }
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/fields", json=data)

    data = r.json
    assert r.status_code == 200
    field_id = data["results"][0]

    data = {
        "name": "Test Field",
        "type": "Numeric",
    }
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/fields", json=data)
    data = r.json
    assert r.status_code == 400

    # get the field by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/fields/{field_id}")
    assert r.status_code == 200
    
    data = r.json
    assert data["results"][0]["id"] == field_id

    # delete the field
    r = client_api2.delete(f"/api2/project/6319f6fb01c844a436e07971/fields/{field_id}")
    print(data)
    r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["results"][0] == field_id
    