import datetime

from bson import ObjectId
from tests.conftest import app, client_api2
import json
from tenjin.database.db import get_db
from urllib import parse


def test_get_column(client_api2):
    """calling this method will create the app fixture which resets the test_db."""
    data = [
        {"id": "6319f87401c844a436e216d3", "name": "Partikel min"},
        {"id": "6319f87401c844a436e216d9", "name": "Partikel max"},
    ]

    # get by id via route
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/column/{data[0]['id']}")
    assert r.status_code == 200
    result = r.json
    assert len(result["results"]) == 1
    assert result["results"][0]["id"] == data[0]["id"]
    assert result["results"][0]["name"] == data[0]["name"]
    assert "values" in result["results"][0]

    query = []
    for d in data:
        query.append(("id", d["id"]))

    # get by id via query string

    url_query = parse.urlencode(query)
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/column?{url_query}")
    assert r.status_code == 200
    result = r.json
    assert len(result["results"]) == 2
    assert result["results"][0]["id"] == data[0]["id"]
    assert result["results"][0]["name"] == data[0]["name"]
    assert result["results"][1]["id"] == data[1]["id"]
    assert result["results"][1]["name"] == data[1]["name"]


def test_post_and_delete_column(client_api2):
    """calling this method will create the app fixture which resets the test_db."""
    data = {
        "name": "Test Column",
        "type": "Numeric",
        "unit": {
            "name": "cm",
        }
    }
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/column", json=data)

    data = r.json
    assert r.status_code == 200
    column_id = data["results"][0]
    
    

    # get the column by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/column/{column_id}")
    assert r.status_code == 200

    data = r.json
    assert data["results"][0]["id"] == column_id

    # delete the column
    r = client_api2.delete(
        f"/api2/project/6319f6fb01c844a436e07971/column/{column_id}"
    )
    print(data)
    r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["results"][0] == column_id
    
    ## Create with Data
    data = {
        "name": "Test Column",
        "type": "Numeric",
        "unit": {
            "name": "cm",
        },
        "values": [1, 2, 3]
    }
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/column", json=data)

    result = r.json
    assert r.status_code == 200
    column_id = result["results"][0]
    
    # delete the column
    r = client_api2.delete(
        f"/api2/project/6319f6fb01c844a436e07971/column/{column_id}"
    )
    print(data)
    r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["results"][0] == column_id
    
    
    ## Create with wrong Data
    data = {
        "name": "Test Column",
        "type": "Numeric",
        "unit": {
            "name": "cm",
        },
        "values": [1, "Hello", 3]
    }
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/column", json=data)

    result = r.json
    assert r.status_code == 400
    assert result["status"] == "error"
