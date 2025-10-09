import datetime

from bson import ObjectId
from tests.conftest import app, client_api2
import json
from tenjin.database.db import get_db
from urllib import parse


def test_get_post_researchitem_and_category(client_api2):
    """calling this method will create the app fixture which resets the test_db.
    The test DB does not contain any research items yet. Thus we must start with creating a research item. Before we can
    create a research item we need to create a research category
    """

    data = {"name": "Test Category", "description": "Test Description"}
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/category", json=data)
    assert r.status_code == 200
    data = r.json
    cat_id = data["results"][0]

    # get the category by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/category/{cat_id}")
    assert r.status_code == 200
    data = r.json
    assert data["results"][0]["id"] == cat_id
    assert data["results"][0]["name"] == "Test Category"
    assert data["results"][0]["description"] == "Test Description"

    # create a research item
    data = {
        "name": "Test Research Item",
        "category": {"id": cat_id},
        "groups": [{"id": "6319f7ce01c844a436e1233e"}],
    }
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/researchitem", json=data)
    assert r.status_code == 200
    data = r.json
    researchitem_id = data["results"][0]

    # get the research item by id
    r = client_api2.get(
        f"/api2/project/6319f6fb01c844a436e07971/researchitem/{researchitem_id}"
    )
    assert r.status_code == 200
    data = r.json
    assert data["results"][0]["id"] == researchitem_id
    assert data["results"][0]["name"] == "Test Research Item"
    assert data["results"][0]["category"]["id"] == cat_id
    assert data["results"][0]["category"]["name"] == "Test Category"

    # delete the research item
    r = client_api2.delete(
        f"/api2/project/6319f6fb01c844a436e07971/researchitem/{researchitem_id}"
    )
    assert r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["results"][0] == researchitem_id

    # delete the category
    r = client_api2.delete(f"/api2/project/6319f6fb01c844a436e07971/category/{cat_id}")
    assert r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["results"][0] == cat_id

    