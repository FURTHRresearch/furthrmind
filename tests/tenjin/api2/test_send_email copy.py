from tests.conftest import app, client_api2

def test_send_mail(client_api2):
    """ calling this method will create the app fixture which resets the test_db. """
    
    # get by field_id of a combobox_field to check the comboboxentries
    
    data = {
        "mail_to": "xxx@furthr-research.com",
        "mail_subject": "Test Email from Furthrmind",
        "mail_body": "This is a test email from Furthrmind server. Please ignore."
    }
    r = client_api2.post(f"/api2/send-email", json=data)

    assert r.status_code == 200
    data = r.json
    assert len(data["results"]) == 1
