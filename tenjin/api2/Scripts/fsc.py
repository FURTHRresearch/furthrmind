import requests
import json

def login(server,email,password):

	login_response = requests.request("POST", server + "/app1/login", headers={},
									  data={"email": email, "password": password})

	header = {
		"Content-Type": "application/json",
		"Cookie": f"session={login_response.cookies.values()[0]}"
	}

	key_response = requests.request("POST", server + "/api2/key", headers=header,data={"TTL": 1})
	return {"X-API-KEY": key_response.text}


#please login and use this header in any further request
host = "http://127.0.0.1:5000"
auth_header = login(host,"db@furthr-research.com","db")


response = requests.request("GET",host +f"/api2/Author",headers=auth_header)
for key,value in json.loads(response.text).items():
	print(value)

author = {
	"name":" Test",
	"institution": "Test"
}

response = requests.request("POST",host +f"/api2/author",headers=auth_header,data = json.dumps([author]))
print(response.text)


projectList = [{
	"name":"New Project"
}]
response = requests.request("POST", host +"/api2/project", headers=auth_header, data=json.dumps(projectList))
projectId = json.loads(response.text)[0]
print(projectId)

groupList = [{"name":f"Group {index}"} for index in range(0,10)]
response = requests.request("POST", host +f"/api2/project/{projectId}/group", headers=auth_header, data=json.dumps(groupList))
groupIdList = json.loads(response.text)
print(groupIdList)

itemList = [{
	"name":f"Item{index+1000}",
	"neglect":False,
	"files":[],
	"fielddata":[
		{"fieldname":"Test Text","fieldtype":"SingleLine","value":"Blabla","author":{"name":"Me"}},
		{"fieldname":"Test Numeric","fieldtype":"Numeric","value":10,"unit":"cm"}],
	"groups":[groupIdList[index]],
	"category":"Your category"
} for index in range(0,10)]

response = requests.request("POST", host +f"/api2/project/{projectId}/researchitem", headers=auth_header, data=json.dumps(itemList))
print(response.text)
try:
	itemIdList = json.loads(response.text)
	print(itemIdList)
except:
	pass



response = requests.request("GET",host +f"/api2/researchitem",headers=auth_header)
for key,value in json.loads(response.text).items():
	print(value)


#todo get research items in each group
#todo get research items in project