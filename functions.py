# Imports
import random
import string
import requests
import json
import main
import os
import sys
import time
import detection
import socket
from gpiozero import LED

API_URL = main.API_URL
API_KEY = main.API_KEY

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ID_FILE_PATH = os.path.join(SCRIPT_DIR, "id.txt")

def random_id_generator(max_length=5):
    """
    Generates a random string consisting of letters and digits with a maximum length
    of 5 characters.

    Args:
        max_length (int): The maximum length of the string to generate. Defaults to 5.

    Returns:
        str: A random string of letters and digits with a maximum length of 5 characters.
    """

    return ''.join(random.choices(string.ascii_letters + string.digits, k=max_length))

def get_id_from_file():
    """
    Retrieves the ID from a file. If the file does not exist, generates a new random ID
    and ensures it is unique by checking against a registration API. The new ID is then
    saved to the file.

    Returns:
        str: The ID retrieved from the file or newly generated.
    """

    try:
        with open(ID_FILE_PATH, "r") as f:
            return f.read()
    except FileNotFoundError:
        return None
    
ID = get_id_from_file()
    
def api_call(method, url, data=None, api_key=None):
    # Converts data to JSON if it is not None
    """
    Makes an API call with the specified method, URL, and optional data and API key.

    Args:
        method (str): The HTTP method to use for the API call (GET, POST, PATCH, DELETE).
        url (str): The URL endpoint for the API call.
        data (dict, optional): The data to send with the API call, if applicable. Defaults to None.
        api_key (str, optional): The API key for authentication. Defaults to None.

    Returns:
        requests.Response: The response object from the API call.

    Raises:
        ValueError: If an invalid HTTP method is provided.
    """

    if data:
        data = json.dumps(data)
    
    api_key_params = {"api_key": api_key}

    headers = {
        "Content-Type": "application/json"
    }

    if method == "GET": # Working
        response = requests.get(url, params=api_key_params)
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
    
def is_registered(id):
    """
    Checks if the id is already registered. If not, it will register it.

    Args:
        id (str): The id of the device.

    Returns:
        bool: True if the device is registered, False if not.
    """
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
    """
    Retrieves the operating status of a device with the given id.

    Args:
        id (str): The id of the device.

    Returns:
        bool: The operating status of the device.
    """
    response = api_call(method="GET", url=f"{API_URL}/device/{id}/", api_key=API_KEY)
    return response.json()["operating"]

# This should be deleted in production. It is only for testing purposes
# The operating parameter should only be modified by the mobile application
def update_operating(id, operating):
    data = {
        "operating": operating
    }
    response = api_call(method="PATCH", url=f"{API_URL}/device/{id}/", data=data, api_key=API_KEY)
    return response

def check_status(id):
    """
    Retrieves the status of a device with the given id.

    Args:
        id (str): The id of the device.

    Returns:
        int: The status of the device.
    """

    response = api_call(method="GET", url=f"{API_URL}/device/{id}/", api_key=API_KEY)
    return response.json()["status"]
    
def update_status(id, status):
    """
    Updates the status of a device with the given id.

    Args:
        id (str): The id of the device.
        status (int): The status to update to:
            0: Standby
            1: Weevils found
            2: Weevils attracted
            3: Weevils eliminated
            4: Weevils not found
        

    Returns:
        requests.Response: The response of the API call.
    """

    data = {
        "status": status
    }
    response = api_call(method="PATCH", url=f"{API_URL}/device/{id}/", data=data, api_key=API_KEY)
    return response

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_status():
    clear_console()
    status = ""
    print("ID: ", ID)
    print("Operating: ", is_operating(ID))

    if check_status(ID) == 0:
        status = "Standby"
    elif check_status(ID) == 1:
        status = "Weevils found"
    elif check_status(ID) == 2:
        status = "Weevils attracted"
    elif check_status(ID) == 3:
        status = "Weevils eliminated"
    elif check_status(ID) == 4:
        status = "Weevils not found"

    print("Status: ", status)

def weevil_detection():
    print("Detecting rice weevils...")

    # The detection process will be here
    result = detection.detect_rice_weevil()

    if result:
        update_status(ID, 1)
    else:
        update_status(ID, 4)
        

def weevil_attraction():
    print("Attracting rice weevils...")
    # Process here
    input()
    update_status(ID, 2)

def weevil_elimination():
    print("Attracting and eliminating rice weevils...")
    # Process here
    input()
    update_status(ID, 3)

def start_process():
    led = LED(17)
    led.on()
    print_status()
    weevil_detection()
    print_status()
    # weevil_attraction()
    # print_status()
    weevil_elimination()
    print_status()
    led.off()
    led.close()

def stop_process():
    led =LED(17)
    led.off()
    

def is_connected_to_internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False
