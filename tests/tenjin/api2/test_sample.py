import datetime

from bson import ObjectId
from tests.conftest import app, client_api2
import json
from tenjin.database.db import get_db
from urllib import parse


def test_get_sample(client_api2):
    """calling this method will create the app fixture which resets the test_db."""
    sample_id = '6319f7d001c844a436e1252a'
    sample_id_2 = '6319f7d001c844a436e1256a'

    # get by id via route
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/sample/{sample_id}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == sample_id
    assert data["results"][0]["name"] == 'S019_2'
    assert data["results"][0]["shortid"] == 'smp-v5jr20'

    # get by name via query string
    sample_name = 'S019_2'
    query = []
    query.append(("name", sample_name))
    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/sample?{url_query}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == sample_id
    assert data["results"][0]["name"] == 'S019_2'
    assert data["results"][0]["shortid"] == 'smp-v5jr20'
    assert "linked_samples" in data["results"][0]
    assert "linked_experiments" in data["results"][0]
    assert "datatables" in data["results"][0]
    assert "groups" in data["results"][0]
    assert "linked_researchitems" in data["results"][0]
    assert "fielddata" in data["results"][0]
    assert "files" in data["results"][0]

    fielddata = data["results"][0]["fielddata"]
    assert len(fielddata) == 2
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

    fieldname = 'Anzahl Regenerationszyklen'
    value = "[1, 1]"
    query.append(("fielddata", f"{fieldname}:{value}"))

    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/sample?{url_query}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 13



def test_get_all_sample(client_api2):
    """calling this method will create the app fixture which resets the test_db."""
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/sample")
    assert r.status_code == 200
    data = r.json
    for r in data["results"]:
        assert "id" in r
        assert "name" in r
        assert "shortid" in r
        assert len(r.keys()) == 3


def test_post_and_delete_sample(client_api2):
    """calling this method will create the app fixture which resets the test_db."""
    data = {"name": "Test Sample", "groups": [{"id": "6319f7ce01c844a436e1233e"}]}
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/sample", json=data)

    data = r.json
    assert r.status_code == 200
    sample_id = data["results"][0]

    data = {
        "name": "Test Sample",
    }
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/sample", json=data)
    data = r.json
    assert r.status_code == 400

    # get the sample by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/sample/{sample_id}")
    assert r.status_code == 200

    data = r.json
    assert data["results"][0]["id"] == sample_id
    assert data["results"][0]["name"] == "Test Sample"

    # delete the sample
    r = client_api2.delete(f"/api2/project/6319f6fb01c844a436e07971/sample/{sample_id}")
    print(data)
    r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["results"][0] == sample_id

    # create sample with fielddata
    data = {"name": "Test Sample", "groups": [{"id": "6319f7ce01c844a436e1233e"}]}

    field_name = "Test Field"
    field_type = "Text"

    # create a new fielddata
    fd_data = {
        "fieldname": field_name,
        "fieldtype": field_type,
        "value": "Test Value",
    }
    data["fielddata"] = [fd_data]
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/sample", json=data)

    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1

    sample_id = data["results"][0]

    # get the sample by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/sample/{sample_id}")
    assert r.status_code == 200
    data = r.json
    assert data["results"][0]["id"] == sample_id
    assert data["results"][0]["name"] == "Test Sample"
    assert len(data["results"][0]["fielddata"]) == 1
    assert data["results"][0]["fielddata"][0]["fieldname"] == field_name
    assert data["results"][0]["fielddata"][0]["fieldtype"] == "SingleLine"
    assert data["results"][0]["fielddata"][0]["value"] == "Test Value"

    # add a new fielddata to the sample
    fd_data = {
        "fieldname": "New Field",
        "fieldtype": "Text",
        "value": "New Value",
    }
    fd_data_list = [{"id": data["results"][0]["fielddata"][0]["id"]}, fd_data]
    data = {"id": sample_id, "fielddata": fd_data_list}

    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/sample", json=data)
    assert r.status_code == 200
    data = r.json
    assert "status" in data
    assert data["status"] == "ok"
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    assert data["results"][0] == sample_id

    # get the sample by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/sample/{sample_id}")
    assert r.status_code == 200
    data = r.json
    assert data["results"][0]["id"] == sample_id
    assert data["results"][0]["name"] == "Test Sample"
    assert len(data["results"][0]["fielddata"]) == 2

    # delete the sample
    r = client_api2.delete(f"/api2/project/6319f6fb01c844a436e07971/sample/{sample_id}")
    assert r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["results"][0] == sample_id


    # create sample with datatables
    data = {"name": "Test Sample", "groups": [{"id": "6319f7ce01c844a436e1233e"}]}
    datatable = {
        "name": "dt",
    }
    data["datatables"] = [datatable]
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/sample", json=data)
    assert r.status_code == 200
    data = r.json
    sample_id = data["results"][0]

    # get the sample by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/sample/{sample_id}")
    assert r.status_code == 200
    data = r.json
    assert data["results"][0]["id"] == sample_id
    assert data["results"][0]["datatables"][0]["name"] == "dt"
    
    
    # delete the sample
    r = client_api2.delete(f"/api2/project/6319f6fb01c844a436e07971/sample/{sample_id}")
    assert r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["results"][0] == sample_id
    
    # create sample and link with an experiment
    data = {"name": "Test Sample", "groups": [{"id": "6319f7ce01c844a436e1233e"}], "experiments": [{"id": "6319f7f801c844a436e1615f"}]}
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/sample", json=data)
    data = r.json
    assert r.status_code == 200
    sample_id = data["results"][0]
    
    # get the sample by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/sample/{sample_id}")
    assert r.status_code == 200
    data = r.json
    data["results"][0]["linked_experiments"][0]["id"] = "6319f7f801c844a436e1615f"
    
    # delete the sample
    r = client_api2.delete(f"/api2/project/6319f6fb01c844a436e07971/sample/{sample_id}")
    assert r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["results"][0] == sample_id