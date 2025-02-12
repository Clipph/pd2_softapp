# Imports
import functions as f

API_URL = "https://calify.pythonanywhere.com/api"
API_KEY = "bd8e4d538dfa993960152da646"

def main():
    id = f.get_id_from_file()
    print("ID:", id)

    if f.is_registered(id):
        print("The id is already registered")
    else:
        print("The id is now registered")

    f.update_operating(id, True)
    print("Is operating?", f.is_operating(id))
    f.update_status(id, 1)
    print("Status:", f.check_status(id))

if __name__ == "__main__":
    main()