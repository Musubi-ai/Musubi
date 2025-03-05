import requests

try:
    res = requests.post("http://127.0.0.1:5000/shutdown")
except requests.exceptions.ConnectionError as e:
    print("Shut")