from tests.conftest import app, client_api2

def test_get_combo(client_api2):
    """ calling this method will create the app fixture which resets the test_db. """
    
    # get by field_id of a combobox_field to check the comboboxentries
    
   
    combo_id = "6319f76601c844a436e0b413"
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/comboboxentry/{combo_id}")
    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == combo_id
    assert data["results"][0]["name"] == "Test"
    
    
def test_get_all_combo(client_api2):
    """ calling this method will create the app fixture which resets the test_db. """
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/comboboxentry")
    assert r.status_code == 200
    data = r.json
    for r in data["results"]:
        assert "id" in r
        assert "name" in r
        assert "fielddata" in r
        assert "field" in r


def test_post_and_delete_combo(client_api2):
    
    field_id_combo = "6319f76301c844a436e0b14c"
    """ calling this method will create the app fixture which resets the test_db. """
    data = {
        "name": "Test ComboEntry",
        "field": {"id": field_id_combo}
    }
    r = client_api2.post(f"/api2/project/6319f6fb01c844a436e07971/comboboxentry", json=data)

    data = r.json
    assert r.status_code == 200
    combo_id = data["results"][0]


    # get the field by id
    r = client_api2.get(f"/api2/project/6319f6fb01c844a436e07971/comboboxentry/{combo_id}")
    assert r.status_code == 200
    
    data = r.json
    assert data["results"][0]["id"] == combo_id

    # delete the field
    r = client_api2.delete(f"/api2/project/6319f6fb01c844a436e07971/comboboxentry/{combo_id}")
    print(data)
    r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["results"][0] == combo_id
    