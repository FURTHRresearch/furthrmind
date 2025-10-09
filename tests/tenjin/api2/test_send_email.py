from tests.conftest import app, client_api2

def test_get_user(client_api2):
    """ calling this method will create the app fixture which resets the test_db. """
    
    # get by field_id of a combobox_field to check the comboboxentries
    
   
    r = client_api2.get(f"/api2/user")

    assert r.status_code == 200
    data = r.json
    user_id = data["results"][0]["id"]
    email = data["results"][0]["email"]
    
    r = client_api2.get(f"/api2/user/{user_id}")
    assert r.status_code == 200
    data = r.json
    assert data["results"][0]["id"] == user_id
    assert data["results"][0]["email"] == email
