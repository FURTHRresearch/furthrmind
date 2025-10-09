import requests
import json


host = "http://127.0.0.1:5000"
auth_header = {"X-API-KEY": "your api key"}


response = requests.request("GET",host +f"/api2/author",headers=auth_header)
for key,value in json.loads(response.text).items():
	print(value)

response = requests.request("GET",host +f"/api2/researchitem",headers=auth_header)
for key,value in json.loads(response.text).items():
	print(value)