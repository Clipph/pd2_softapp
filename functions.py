# Imports
import random
import string
import requests
import json
import main

API_URL = main.API_URL
API_KEY = main.API_KEY

def random_id_generator(max_length=5):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=max_length))

def get_id_from_file():
    try:
        with open("id.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        id = random_id_generator()
        with open("id.txt", "w") as f:
            f.write(id)
        return id
    
def api_call(method, url, data=None, params=None, api_key=None):
    # Converts data to JSON if it is not None
    if data:
        data = json.dumps(data)
    
    api_key_params = {"api_key": api_key}

    headers = {
        "Content-Type": "application/json"
    }

    if method == "GET": # Working
        response = requests.get(url, params=api_key_params)
        print(response.request.url)
        return response
    elif method == "POST": # Working
        response = requests.post(url, data=data, headers=headers, params=api_key_params)
        return response
    elif method == "PATCH": # Working
        response = requests.patch(url, data=data, headers=headers, params=api_key_params)
        return response
    elif method == "DELETE": # Working
        response = requests.delete(url, data=data, headers=headers, params=api_key_params)
        return response
    else:
        raise ValueError("Invalid method")
    
# Checks if the id is already registered. If not, it will register it
def is_registered(id):
    register_id = {
        "id": id
    }
    response = api_call(method="GET", url=f"{API_URL}/device/{id}/", api_key=API_KEY)
    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        response = api_call(method="POST", url=f"{API_URL}/register_device/", data=register_id, api_key=API_KEY)
        return False

def is_operating(id):
    response = api_call(method="GET", url=f"{API_URL}/device/{id}/", api_key=API_KEY)
    return response.json()["operating"]
    
def update_status(id, status):
    data = {
        "status": status
    }
    response = api_call(method="PATCH", url=f"{API_URL}/device/{id}/", data=data, api_key=API_KEY)
    return response