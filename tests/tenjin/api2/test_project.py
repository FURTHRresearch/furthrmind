import datetime

from bson import ObjectId
from tests.conftest import app, client_api2
import json
from tenjin.database.db import get_db
from urllib import parse

def test_get_project(client_api2):
    """ calling this method will create the app fixture which resets the test_db. """
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971")
    assert r.status_code == 200
    data = r.json
    print(data)
    
def test_get_all_project(client_api2):
    """ calling this method will create the app fixture which resets the test_db. """
    r = client_api2.get(f"/api2/projects")
    assert r.status_code == 200
    data = r.json
    for r in data["results"]:
        assert "id" in r
        assert "name" in r
        assert "info" in r
        assert len(r.keys()) == 3
    
    
    
    
def test_get_many_projects(client_api2):
    # test for one id
    query = []
    query.append(("id", "6319f6fb01c844a436e07971"))    
    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/projects?{url_query}")
    assert r.status_code == 200
    
    data = r.json
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == "6319f6fb01c844a436e07971"
    assert "experiments" in data["results"][0]
    assert "samples" in data["results"][0]
    assert "researchitems" in data["results"][0]
    assert data["results"][0]["researchitems"] == {}
    assert "permissions" in data["results"][0]
    assert "id" in data["results"][0]
    assert "shortID" in data["results"][0]
    assert data["results"][0]["shortID"] == 'prj-gv4lqs'
    assert "name" in data["results"][0]
    assert data["results"][0]["name"] == "Maskentests_1"
    assert "units" in data["results"][0]
    assert len(data["results"][0]["units"]) == 159 
    assert "fields" in data["results"][0]
    assert "groups" in data["results"][0]
    
    # test for wrong name
    query = []
    query.append(("name", "Maskentest_1"))    # Maskentests_1 is the correct name 
    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/projects?{url_query}")
    assert r.status_code == 400
    
    
    # test for correct name
    query = []
    query.append(("name", "Maskentests_1"))    # Maskentests_1 is the correct name 
    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/projects?{url_query}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == "6319f6fb01c844a436e07971"
    assert "experiments" in data["results"][0]
    assert "samples" in data["results"][0]
    assert "researchitems" in data["results"][0]
    assert data["results"][0]["researchitems"] == {}
    assert "permissions" in data["results"][0]
    assert "id" in data["results"][0]
    assert "shortID" in data["results"][0]
    assert data["results"][0]["shortID"] == 'prj-gv4lqs'
    assert "name" in data["results"][0]
    assert data["results"][0]["name"] == "Maskentests_1"
    assert "units" in data["results"][0]
    assert len(data["results"][0]["units"]) == 159 
    assert "fields" in data["results"][0]
    assert "groups" in data["results"][0]
    
    # test for shortID
    query = []
    query.append(("shortid", "prj-gv4lqs"))    
    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/projects?{url_query}")
    assert r.status_code == 200
    
    data = r.json
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == "6319f6fb01c844a436e07971"
    assert "experiments" in data["results"][0]
    assert "samples" in data["results"][0]
    assert "researchitems" in data["results"][0]
    assert data["results"][0]["researchitems"] == {}
    assert "permissions" in data["results"][0]
    assert "id" in data["results"][0]
    assert "shortID" in data["results"][0]
    assert data["results"][0]["shortID"] == 'prj-gv4lqs'
    assert "name" in data["results"][0]
    assert data["results"][0]["name"] == "Maskentests_1"
    assert "units" in data["results"][0]
    assert len(data["results"][0]["units"]) == 159 
    assert "fields" in data["results"][0]
    assert "groups" in data["results"][0]
    
def test_post_and_delete_project(client_api2):
    """ calling this method will create the app fixture which resets the test_db. """
    data = {
        "name": "Test Project",
        "info": "Bla",


    }
    r = client_api2.post(f"/api2/projects", json=data)
    assert r.status_code == 200
    data = r.json
    print(data)
    
    r = client_api2.delete(f"/api2/project/{data["results"][0]}")
    