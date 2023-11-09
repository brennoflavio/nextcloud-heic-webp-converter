import logging
from webdav3.client import Client
from tempfile import NamedTemporaryFile
from dotenv import load_dotenv
import os
from urllib.parse import urlparse
from tempfile import NamedTemporaryFile
import subprocess

load_dotenv()
logging.basicConfig(level=logging.INFO)

def get_client():
    options = {
        "webdav_hostname": os.getenv("NEXTCLOUD_DAV_ENDPOINT"),
        "webdav_login": os.getenv("NEXTCLOUD_USERNAME"),
        "webdav_password": os.getenv("NEXTCLOUD_PASSWORD"),
    }
    client = Client(options)
    return client

def sanitize_path(path):
    path_to_strip = urlparse(os.getenv("NEXTCLOUD_DAV_ENDPOINT")).path
    return "/" + path.replace(path_to_strip, "")


def expand_directory(folder, client):
    files = []
    file_list = client.list(folder, get_info=True)

    for file in file_list:
        file["path"] = sanitize_path(file["path"])
        if file["path"] == folder:
            continue
        if file.get("isdir"):
            files.extend(expand_directory(file["path"], client))
        else:
            files.append(file)

    return [x for x in files if not x.get("isdir")]

def download_file(remote_path, local_path, client):
    return client.download_sync(remote_path=remote_path, local_path=local_path)

def check_file(remote_path, client):
    return client.check(remote_path)

def upload_file(remote_path, local_path, client):
    return client.upload_sync(remote_path=remote_path, local_path=local_path)

def delete_file(remote_path, client):
    return client.clean(remote_path)

def change_file_extension(file_path, new_extension):
    head, tail = os.path.split(file_path)
    filename, _ = os.path.splitext(tail)
    return os.path.join(head, f"{filename}.{new_extension}")

def get_file_extension(file_path):
    _, tail = os.path.split(file_path)
    _, ext = os.path.splitext(tail)
    return ext[1:]

def convert_file(heic_file):
    logging.info(f"Converting {heic_file}")
    subprocess.run(["heic2jpg", "-s", heic_file, "--keep"])
    return change_file_extension(heic_file, "jpg")

def main():
    client = get_client()
    assert client

    folder = os.getenv("NEXTCLOUD_FOLDER")
    assert folder

    files = expand_directory(folder, client)
    files = [sanitize_path(x["path"]) for x in  files]
    files = [x for x in  files if get_file_extension(x) == "heic"]
    logging.info(f"Going to do {len(files)}")

    for f in files:
        if not check_file(f):
            continue

        with NamedTemporaryFile("w+", suffix=".heic") as temp_file:
            download_file(f, temp_file.name, client)
            new_file = convert_file(temp_file.name)
            new_remote_path = change_file_extension(f, "jpg")
            logging.info(f"Converting {f} to {new_remote_path}")
            upload_file(new_remote_path, new_file, client)
            delete_file(f, client)

if __name__ == "__main__":
    main()
