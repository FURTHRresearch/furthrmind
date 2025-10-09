import datetime

from bson import ObjectId
from tests.conftest import app, client_api2
import json
from tenjin.database.db import get_db
from urllib import parse

def test_get_group(client_api2):
    """ calling this method will create the app fixture which resets the test_db. """
    group_id = '6319f7ce01c844a436e1233e'
    
    # get by id via route
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/groups/{group_id}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == group_id
    assert data["results"][0]["name"] == "3M - 9501V+"
    assert data["results"][0]["shortid"] == 'grp-gxcyrx'
    
    # get by name via query string
    group_name = "3M - 950fasd"
    query = []
    query.append(("name", group_name))   
    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/groups?{url_query}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == group_id
    assert data["results"][0]["name"] == "3M - 9501V+"
    assert data["results"][0]["shortid"] == 'grp-gxcyrx'
    assert "samples" in data["results"][0]
    assert "experiments" in data["results"][0]
    assert "sub_groups" in data["results"][0]
    assert "parent_group" in data["results"][0]
    assert "researchitems" in data["results"][0]
    assert "fielddata" in data["results"][0]
    
    fielddata = data["results"][0]["fielddata"]
    assert len(fielddata) == 5
    for fd in fielddata:
        assert "fieldname" in fd
        assert "fieldtype" in fd
        assert "value" in fd
        assert "fieldid" in fd
        assert "si_value" in fd
        assert "unit" in fd
        assert "author" in fd
        assert "id" in fd
        
    # filter groups by fielddata
    fieldname = "Hersteller"
    value = "3M"
    query = []
    query.append(("fielddata", f"{fieldname}:{value}"))
    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/groups?{url_query}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 2

    fieldname = "Hersteller"
    value = '6319f76601c844a436e0b495'
    query = []
    query.append(("fielddata", f"{fieldname}:{value}"))
    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/groups?{url_query}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 2
    
    fieldname = 'Produktname'
    value = '9501V+'
    query = []
    query.append(("fielddata", f"{fieldname}:{value}"))
    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/groups?{url_query}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 1
    
    fieldname = 'All masks are measured'
    value = True
    query = []
    query.append(("fielddata", f"{fieldname}:{value}"))
    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/groups?{url_query}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 3


def test_get_all_group(client_api2):
    """ calling this method will create the app fixture which resets the test_db. """
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/groups")
    assert r.status_code == 200
    data = r.json
    for r in data["results"]:
        assert "id" in r
        assert "name" in r
        assert "shortid" in r
        assert len(r.keys()) == 3
    
    
def test_post_and_delete_group(client_api2):
    """ calling this method will create the app fixture which resets the test_db. """
    data = {
        "name": "Test Group",
    }
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/groups", json=data)
    
    data = r.json
    assert r.status_code == 200
    group_id = data["results"][0]
    
    data = {
        "name": "Test Group",
    }
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/groups", json=data)
    data = r.json
    assert r.status_code == 400
    
    # get the group by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/groups/{group_id}")
    assert r.status_code == 200
    
    data = r.json
    assert data["results"][0]["id"] == group_id
    

    # delete the group
    r = client_api2.delete(f"/api2/project/6319f6fb01c844a436e07971/groups/{group_id}")
    print(data)
    r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["results"][0] == group_id
    
    # create group with fielddata
    data = {
        "name": "Test Group",
    }
    
    field_name = "Test Field"
    field_type = "Text"
    
    # create a new fielddata
    fd_data = {
        "fieldname": field_name,
        "fieldtype": field_type,
        "value": "Test Value",
    }
    data["fielddata"] = [fd_data]
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/groups", json=data)
    
    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1 
    
    group_id = data["results"][0]
    
    # get the group by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/groups/{group_id}")
    assert r.status_code == 200
    data = r.json
    assert data["results"][0]["id"] == group_id
    assert data["results"][0]["name"] == "Test Group"
    assert len(data["results"][0]["fielddata"]) == 1
    assert data["results"][0]["fielddata"][0]["fieldname"] == field_name
    assert data["results"][0]["fielddata"][0]["fieldtype"] == "SingleLine"
    assert data["results"][0]["fielddata"][0]["value"] == "Test Value"

    # add a new fielddata to the group
    fd_data = {
        "fieldname": "New Field",
        "fieldtype": "Text",
        "value": "New Value",
    }
    fd_data_list = [{"id": data["results"][0]["fielddata"][0]["id"]}, fd_data]
    data = {"id": group_id, "fielddata": fd_data_list}
    
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/groups", json=data)
    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    assert data["results"][0] == group_id
    
    # get the group by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/groups/{group_id}")
    assert r.status_code == 200
    data = r.json
    assert data["results"][0]["id"] == group_id
    assert data["results"][0]["name"] == "Test Group"
    assert len(data["results"][0]["fielddata"]) == 2
    
    # delete the group
    r = client_api2.delete(f"/api2/project/6319f6fb01c844a436e07971/groups/{group_id}")
    assert r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["results"][0] == group_id
