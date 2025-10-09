import time

import requests
import json
host = "http://127.0.0.1:5000"

auth_header = {"X-API-KEY": "TQGMX10H94TNH574UYYN1PLEXQ5BE93N"}
session = requests.session()
session.headers.update(auth_header)

start = time.time()

response = session.get(f"{host}/api2/project")
result = response.json()
lbl = result["results"][0]
exp = lbl.get("experiments")
print(len(exp))
exp_id = exp[0]["id"]
print(exp_id)
response = session.get(f"{host}/api2/project/{lbl.get('id')}/experiment")
result = response.json()
print(len(result["results"]))

response = session.get(f"{host}/api2/project/{lbl.get('id')}/experiment/{exp_id}")
result = response.json()
result_1 = result["results"]
print(result["results"])

response = session.get(f"{host}/api2/experiment/{exp_id}")
result = response.json()
result_2 = result["results"]
print(result["results"])

print(time.time()-start)

