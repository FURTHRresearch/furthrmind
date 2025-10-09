import datetime

from bson import ObjectId
from tests.conftest import app, client
import json
from tenjin.database.db import get_db

def test_prepare(client):
    """ calling this method will create the app fixture which resets the test_db. """


def test_get_clipboard_string(client):
    
    r = client.get(f"/projects/6319f6fb01c844a436e07971/experiment/6319f7db01c844a436e13890/copy-clipboard")
    assert r.status_code == 200
    data = r.text
    print(data)


    # expected_output = "Name\t3M - Aura 9322+_S004_Maskentest\nid\t6319f7db01c844a436e13890\nshortId\texp-zaql15\nCategory\tExperiment\nDurchlass\tRawDataCalc\tP\t21.16\tAerosol conc [mg/m³]\t22.65\t\nDatum\tDate\t2020-04-15T08:45:55\t\nAnzahl Regenerationszyklen\tNumeric\t1.0\tNone\tSI Value\t1.0\t\nDifferenzdruck Kammer\tNumeric\t6.8\tmbar\tSI Value\t680.0\t\nDifferenzdruck Maske\tNumeric\t32.9\tmbar\tSI Value\t3290.0\t\nDifferenzdruck ohne Maske\tNumeric\t31.2\tmbar\tSI Value\t3120.0\t\nVolumenstrom\tNumeric\t94.7\tL/min\tSI Value\t0.00158\t\nNozzle Pressure\tNumeric\t200.0\tmbar\tSI Value\t20000.0\t\nNaCl Konzentration\tNumeric\t3.0\tw%\tSI Value\t3.0\t\nSetup\tComboBox\tMaskenteststand v1.0\t\nMaskenhalter\tComboBox\tMaennlicher_Kopf - V1\t\nOptische Mängel\tMultiLine\t--\t\nAnmerkungen\tMultiLine\t"AVT" auf Maske gekennzeichnet gewesen\t\nLinked Items\nAnzahl Regenerationszyklen\tNumeric\t--\t\nCharge\tComboBox\tSterilisation 1\t\n"

