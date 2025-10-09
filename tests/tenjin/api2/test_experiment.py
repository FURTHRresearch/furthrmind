import datetime

from bson import ObjectId
from tests.conftest import app, client_api2
import json
from tenjin.database.db import get_db
from urllib import parse


def test_get_experiment(client_api2):
    """calling this method will create the app fixture which resets the test_db."""
    exp_id = "6319f7f801c844a436e1615f"

    # get by id via route
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/experiment/{exp_id}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == exp_id
    assert data["results"][0]["name"] == "3M - 9501V+_3M_fake_3_Maskentest"
    assert data["results"][0]["shortid"] == "exp-ge08js"

    # get by name via query string
    exp_name = "3M - 9501V+_3M_fake_3_Maskentest"
    query = []
    query.append(("name", exp_name))
    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/experiment?{url_query}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == exp_id
    assert data["results"][0]["name"] == "3M - 9501V+_3M_fake_3_Maskentest"
    assert data["results"][0]["shortid"] == "exp-ge08js"
    assert "linked_samples" in data["results"][0]
    assert "linked_experiments" in data["results"][0]
    assert "datatables" in data["results"][0]
    assert "groups" in data["results"][0]
    assert "linked_researchitems" in data["results"][0]
    assert "fielddata" in data["results"][0]
    assert "files" in data["results"][0]

    fielddata = data["results"][0]["fielddata"]
    assert len(fielddata) == 13
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
    query = []

    fieldname = "Druck Kammer"
    value = "[4, 5, mbar]"
    query.append(("fielddata", f"{fieldname}:{value}"))

    fieldname = "Differenzdruck Maske"
    value = "[1, 2, mbar]"
    query.append(("fielddata", f"{fieldname}:{value}"))
    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/experiment?{url_query}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 11

    fieldname = "Datum"
    start_date = datetime.datetime(2020, 5, 8, 0, 0, 0)
    end_date = datetime.datetime(2020, 5, 8, 23, 59, 59)
    value = f"[{start_date.isoformat()},{end_date.isoformat()}]"
    query = []
    query.append(("fielddata", f"{fieldname}:{value}"))
    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/experiment?{url_query}")
    data = r.json
    assert r.status_code == 200
    assert len(data["results"]) == 9


def test_get_all_experiment(client_api2):
    """calling this method will create the app fixture which resets the test_db."""
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/experiment")
    assert r.status_code == 200
    data = r.json
    for r in data["results"]:
        assert "id" in r
        assert "name" in r
        assert "shortid" in r
        assert len(r.keys()) == 3


def test_post_and_delete_experiment(client_api2):
    """calling this method will create the app fixture which resets the test_db."""
    data = {"name": "Test Experiment", "groups": [{"id": "6319f7ce01c844a436e1233e"}]}
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/experiment", json=data)

    data = r.json
    assert r.status_code == 200
    exp_id = data["results"][0]

    data = {
        "name": "Test Experiment",
    }
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/experiment", json=data)
    data = r.json
    assert r.status_code == 400

    # get the experiment by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/experiment/{exp_id}")
    assert r.status_code == 200

    data = r.json
    assert data["results"][0]["id"] == exp_id
    assert data["results"][0]["name"] == "Test Experiment"

    # delete the experiment
    r = client_api2.delete(f"/api2/project/6319f6fb01c844a436e07971/experiment/{exp_id}")
    print(data)
    r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["results"][0] == exp_id

    # create experiment with fielddata
    data = {"name": "Test Experiment", "groups": [{"id": "6319f7ce01c844a436e1233e"}]}

    field_name = "Test Field"
    field_type = "Text"

    # create a new fielddata
    fd_data = {
        "fieldname": field_name,
        "fieldtype": field_type,
        "value": "Test Value",
    }
    data["fielddata"] = [fd_data]
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/experiment", json=data)

    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1

    exp_id = data["results"][0]

    # get the experiment by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/experiment/{exp_id}")
    assert r.status_code == 200
    data = r.json
    assert data["results"][0]["id"] == exp_id
    assert data["results"][0]["name"] == "Test Experiment"
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
    data = {"id": exp_id, "fielddata": fd_data_list}

    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/experiment", json=data)
    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    assert data["results"][0] == exp_id

    # get the experiment by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/experiment/{exp_id}")
    assert r.status_code == 200
    data = r.json
    assert data["results"][0]["id"] == exp_id
    assert data["results"][0]["name"] == "Test Experiment"
    assert len(data["results"][0]["fielddata"]) == 2

    # delete the experiment
    r = client_api2.delete(f"/api2/project/6319f6fb01c844a436e07971/experiment/{exp_id}")
    assert r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["results"][0] == exp_id

    
    # create experiment with datatables
    data = {"name": "Test Experiment", "groups": [{"id": "6319f7ce01c844a436e1233e"}]}
    datatable = {
        "name": "dt",
    }
    data["datatables"] = [datatable]
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/experiment", json=data)
    assert r.status_code == 200
    data = r.json
    exp_id = data["results"][0]
    
    # get the experiment by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/experiment/{exp_id}")
    assert r.status_code == 200
    data = r.json
    assert data["results"][0]["id"] == exp_id
    assert data["results"][0]["datatables"][0]["name"] == "dt"
    
    
    # delete the experiment
    r = client_api2.delete(f"/api2/project/6319f6fb01c844a436e07971/experiment/{exp_id}")
    assert r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["results"][0] == exp_id
    