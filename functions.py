# Imports
import random
import string

def random_id_generator(max_length=5):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=max_length))