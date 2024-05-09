import random
import string


def generateRandomFileName(file):
    name = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=64))
    file_type = file.filename.split('.')[-1]
    name += '.' + file_type
    return name
