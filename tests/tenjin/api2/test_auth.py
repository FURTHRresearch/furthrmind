from tests.conftest import app, client_api2, client_api2_wrong_key

def test_auth(client_api2):
    """ calling this method will create the app fixture which resets the test_db. """
    
    # get by field_id of a combobox_field to check the comboboxentries


    r = client_api2.get(f"/api2/project")
    assert r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    
def test_auth(client_api2_wrong_key):
    """ calling this method will create the app fixture which resets the test_db. """
    
    # get by field_id of a combobox_field to check the comboboxentries


    r = client_api2_wrong_key.get(f"/api2/project")
    assert r.status_code == 401

