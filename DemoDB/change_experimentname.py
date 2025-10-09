import os
import requests
import json
import pandas as pd
# Login zum FURTHRmind Server:
#
# Auslesen des API Keys (nicht weitergeben):
# home = os.path.expanduser("~")
# with open(f"{home}/dev_api.txt") as f:
#     api_key = f.read()

api_key = "LW8UDU23IGZ800O6OJYWS8H7IZ0C0T66"

# Login
host = 'http://127.0.0.1:5000'
session = requests.session()
session.headers.update({"X-API-KEY": api_key})

# Definiere in welchem Projekt die Experimente sind:
projectId ="6319f6fb01c844a436e07971"

project = session.get(f"{host}/api2/project/{projectId}")
expList = project.json()["results"][0]["experiments"]

to_remove = ["UKA - ", "UK-Köln - ", "Städteregion - ", "Hornbach - ", "Hage-Werken - ", "Makrite - "]
for experiment in expList:
    for word in to_remove:
        if word in experiment["name"]:
            print("Old name: ", experiment["name"] )
            experiment["name"] = experiment["name"].replace(word, '')
            print("New name: ", experiment["name"])

            experiment_id = experiment["id"]
            updated_exp = {
                "id": experiment_id,
                "name": experiment["name"],
            }
            print(updated_exp)

            response = session.post(f"{host}/api2/project/{projectId}/experiment", data=json.dumps(updated_exp))

            print(response)

print(expList)