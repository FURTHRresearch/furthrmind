import requests
host = "http://127.0.0.1:5000"

session = requests.session()
response = session.get(f"{host}/api2/experiment/test")
# response = session.get(f"{host}/project")
print(response.json())
