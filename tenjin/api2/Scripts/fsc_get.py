import time

import requests
import json
host = "https://fsc.furthrmind.app"

auth_header = {"X-API-KEY": "568PB3JF3MU3J7JE9XZSR30LSVMC832C"}
start = time.time()
response = requests.request("GET", host +f"/api2/researchitems", headers=auth_header)
for key,value in json.loads(response.text).items():
	print(value)
print(time.time()-start)
