# Imports
import random
import string

def random_id_generator(max_length=5):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=max_length))

# Make a function that retrieves a string from a file. The file is called "id.txt" and contains a single string.
# If the function didn't see the file existing, it should create the file and write a random string to it using the function from the previous task.

def get_id_from_file():
    try:
        with open("id.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        id = random_id_generator()
        with open("id.txt", "w") as f:
            f.write(id)
        return id