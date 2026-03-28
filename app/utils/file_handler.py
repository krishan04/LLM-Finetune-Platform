import os

BASE_PATH = "storage/datasets/"

def save_file(file):
    os.makedirs(BASE_PATH, exist_ok=True)

    file_path = os.path.join(BASE_PATH, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return file_path
