import datetime

from bson import ObjectId
from tests.conftest import app, client_api2
import json
from tenjin.database.db import get_db
from urllib import parse

def test_get_datatable(client_api2):
    """ calling this method will create the app fixture which resets the test_db. """
    

    datatable_id = '6319fe0601c844a436e48097'
    
    # get by id via route
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/datatable/{datatable_id}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == datatable_id
    assert data["results"][0]["name"] == "Data table"
    assert "columns" in data["results"][0]
    assert len(data["results"][0]["columns"]) == 111
    
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/datatable")
    assert r.status_code == 200
    data = r.json

    for d in data["results"]:
        assert "id" in d
        assert "name" in d

    id_list = [d["id"] for d in data["results"][0:3]]

    query = []
    for _id in id_list:
        query.append(("id", _id))

    # get by id via query string

    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/datatable?{url_query}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 3


def test_post_and_delete_datatable(client_api2):
    """ calling this method will create the app fixture which resets the test_db. """
    data = {
        "name": "Test DataTable",
    }
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/datatable", json=data)

    data = r.json
    assert r.status_code == 200
    datatable_id = data["results"][0]

    # get the datatable by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/datatable/{datatable_id}")
    assert r.status_code == 200
    
    data = r.json
    assert data["results"][0]["id"] == datatable_id

    # delete the datatable
    r = client_api2.delete(f"/api2/project/6319f6fb01c844a436e07971/datatable/{datatable_id}")
    print(data)
    r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["results"][0] == datatable_id
    