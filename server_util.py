from os import path, mkdir, listdir, unlink, makedirs
from shutil import rmtree
import string
import random
from statuses import *
import requests

URL = "http://mritopet.pythonanywhere.com/get_val"

app_root = path.dirname(path.abspath(__file__))

counter = [-1]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def create_folders():
    input_folder = path.join(app_root, 'input')
    if not path.exists(input_folder):
        mkdir(input_folder)
        mkdir(path.join(input_folder, "nii"))
        mkdir(path.join(input_folder, "img"))

    temp_folder = path.join(input_folder, 'temp')
    if not path.exists(temp_folder):
        mkdir(temp_folder)
        mkdir(path.join(temp_folder, "denoise"))
        mkdir(path.join(temp_folder, "skull_strip"))
        mkdir(path.join(temp_folder, "bias_cor"))
        mkdir(path.join(temp_folder, "output"))

    output_folder = path.join(app_root, 'output')
    if not path.exists(output_folder):
        mkdir(output_folder)
        mkdir(path.join(output_folder, "nii"))
        mkdir(path.join(output_folder, "img"))


def delete_contents(folder_path):
    folder = folder_path
    for filename in listdir(folder):
        file_path = path.join(folder, filename)
        try:
            if path.isfile(file_path) or path.islink(file_path):
                unlink(file_path)
            elif path.isdir(file_path):
                rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s : %s' % (file_path, e))

    rmtree(folder)


def supported_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext == "nii":
        return True
    else:
        return False


def aggregate(val=None):
    r = requests.get(url = URL)
    data = r.json()
      
    return data




def generate_secret_key():
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return str(res)
