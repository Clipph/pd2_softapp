# Imports
import functions as f

API_URL = "https://calify.pythonanywhere.com/api"
API_KEY = "bd8e4d538dfa993960152da646"

def main():
    id = f.get_id_from_file()
    
    # api = f.api_call(method="GET", url=f"{API_URL}/device/{id}/", api_key=API_KEY) -- this works
    # api = f.api_call(method="POST", url=f"{API_URL}/register_device/", data=register_id, api_key=API_KEY) -- this works
    # api = f.api_call(method="PATCH", url=f"{API_URL}/device/{id}/", data=data, api_key=API_KEY) -- this works
    # api = f.api_call(method="DELETE", url=f"{API_URL}/device/{id}/", api_key=API_KEY) -- this works

if __name__ == "__main__":
    main()