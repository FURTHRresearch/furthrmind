import datetime

from bson import ObjectId
from tests.conftest import app, client
import json
from tenjin.database.db import get_db

def test_prepare(client):
    """ calling this method will create the app fixture which resets the test_db. """


def test_get_page_item_index(client):
    dataview_id = ObjectId("673744e861f66e910c21b037")
    r = client.get(f"/dataviews/{dataview_id}/page-item-index-from-db")
    assert r.status_code == 200
    data = r.json
    assert data["maxPage"] == 3
    assert len(data["pageItemMapping"][str(3)]) == 74

def test_get_chart_update_time(client):
    datetime.datetime.now(tz=datetime.UTC)
    dataview_id = ObjectId("673744e861f66e910c21b037")
    r = client.get(f'/dataviews/{dataview_id}/updated')
    assert r.status_code == 200
    assert r.text.startswith("2024-11-15T12:56:27") == True

def test_get_chart_data(client):
    dataview_id = ObjectId("673744e861f66e910c21b037")
    r = client.get(f"/dataviews/{dataview_id}/data")
    assert r.status_code == 200
    data = json.loads(r.text)
    assert len(data) == 274

def test_get_update_data(client):
    dataview_id = ObjectId("673744e861f66e910c21b037")
    db = get_db().db
    # set Data to empty list to test if data is correctly written to data field in db and if DateUpdate is executed
    db["DataViewChart"].update_one({"DataViewID": dataview_id}, {"$set": {"Data": []}})

    test_get_chart_data(client)
    r = client.get(f'/dataviews/{dataview_id}/updated')
    assert r.status_code == 200
    assert r.text.startswith("Hours") == True

