import json
from numpy import save
from mri2pet import Mri2Pet
from os import path, mkdir, listdir, unlink
#from werkzeug.utils import secure_filename
import dropbox
from statuses import *
import shutil
import os
import time
import zipfile
import string
import base64
import random
import shutil
import sys

from server_util import *
from model_util import *


app_root = path.dirname(path.abspath(__file__))

MESSAGE_EVENT = "Messages"
MRI = "MRI"
PET = "PET"

model = Mri2Pet()
dbx = dropbox.Dropbox(
    "dsD7-kooEwQAAAAAAAAAAQr33QP7twaSOK_Xj9RJHirXh6-h9d7itQsJG-KheXzt")

print(bcolors.BOLD, model, bcolors.ENDC, flush=True)

def download_file(dbx, file, name):
    _, f = dbx.files_download("/" + file)
    out = open(name, 'wb')
    out.write(f.content)
    out.close()
    print(f)


def exists(dbx, path):
    try:
        dbx.files_get_metadata(path)
        return True
    except:
        return False


# def upload_file(dbx, file_path, file):
#     with open(file, "rb") as f:
#         dbx.files_upload(f.read(), file_path,
#                          mode=dropbox.files.WriteMode.overwrite)


def process(model, file_path, Skull_Strip, Denoise, Bias_Correction, status):

    print("Inside Generator")
    print("start")

    print("process_start")
    status['data'][PREPROCESS_START] = True
    emit(status)

    model.process(file_path, Skull_Strip=Skull_Strip,
                  Denoise=Denoise, Bias_Correction=Bias_Correction, emit=emit, status=status, send_mri=send_mri)

    status['data'][PREPROCESS_END] = True
    emit(status)
    print("process_end")

    print("generate_start")
    status['data'][GENERATE_START] = True
    emit(status)

    model.generate(send_pet)

    status['data'][GENERATE_END] = True
    emit(status)
    print("generate_end")

    print("saving_start")
    status['data'][SAVING_START] = True
    emit(status)

    model.save()

    print("saving_start")
    status['data'][SAVING_END] = True
    emit(status)
    print("saving_end")

    print("end")

def mri_to_pet_conversion():
    print("mri to pet conversion started")
    create_folders()
    input_folder = path.join(app_root, 'input', 'nii')
    target_mri = "mri"    
    input_mri_file_path = path.join(input_folder, target_mri + ".nii")
    file_path = input_mri_file_path

    print(bcolors.OKBLUE + f"File path : {file_path}" + bcolors.ENDC)

    status = dict()
    status['id'] = "PROCESS_STATUS"
    status['data'] = dict()

    status['data'][PREPROCESS_START] = False
    status['data'][PREPROCESS_END] = False
    status['data'][GENERATE_START] = False
    status['data'][GENERATE_END] = False
    status['data'][SAVING_START] = False
    status['data'][SAVING_END] = False
    status['data'][DENOISE] = False
    status['data'][SKULL_STRIP] = False
    status['data'][BIAS_CORRECTION] = False
    status['data'][UPLOAD_START] = False
    status['data'][UPLOAD_END] = False
    print("********************************"+file_path)
    process(model, file_path, Skull_Strip=True,
                Denoise=True, Bias_Correction=True, status=status)

    # status['data'][UPLOAD_START] = True
    # emit(status)
    # pet_zip_upload = dict()
    # pet_zip_upload['id'] = "PET_ZIP_UPLOAD"
    # pet_zip_upload['data'] = dict()
    # pet_zip = shutil.make_archive(path.join(
    #     app_root, 'output', "pet"), 'zip', path.join(app_root, 'output', "nii"))
    # upload_file(dbx, "/pet.zip", pet_zip)
    # pet_zip_upload['data']['uploaded'] = True
    # try:
    #     pet_zip_upload['data']['url'] = dbx.sharing_create_shared_link_with_settings(
    #         "/pet.zip").url
    # except:
    #     pet_zip_upload['data']['url'] = dbx.sharing_list_shared_links(
    #         "/pet.zip", direct_only=True).url

    # emit(pet_zip_upload)

    # status['data'][UPLOAD_END] = True
    # emit(status)

    # if json_message['id'] == 'DELETE_STATUS' and json_message['data']['delete'] or json_message['id'] == "START" and json_message['data']['start_server']:

    #     print(bcolors.WARNING +
    #           "DELETING LOCAL FOLDERS AND REMOTE FILES" + bcolors.ENDC)

    #     if exists(dbx, "/pet.zip"):
    #         dbx.files_delete("/pet.zip")
    #     if exists(dbx, "/mri.zip"):
    #         dbx.files_delete("/mri.zip")

    #     if path.isdir("input"):
    #         delete_contents(path.join(app_root, "input"))
    #     if path.isdir("output"):
    #         delete_contents(path.join(app_root, "output"))

    print("mri to pet conversion done")
    return 'hello'  # response    


def emit(data):
    #socketio.emit(MESSAGE_EVENT, json.dumps(data))
    print(data)


def send_mri(folder):
    mr_slice_no = 0
    for img in sorted(listdir(folder)):
        mr_slice = dict()
        with open(path.join(folder, img), "rb") as image_file:
            encoded_string = base64.b64encode(
                image_file.read()).decode('utf-8')
            mr_slice['slice_no'] = mr_slice_no
            mr_slice['data'] = encoded_string

            #socketio.emit(MRI, json.dumps(mr_slice))
            print(json.dumps(mr_slice))
        mr_slice_no += 1

    mri_img_upload = dict()
    mri_img_upload['id'] = "MRI_IMG_UPLOAD"
    mri_img_upload['data'] = dict()
    mri_img_upload['data']['total_slice_number'] = len(listdir(folder))
    mri_img_upload['data']['uploaded'] = True

    emit(mri_img_upload)


def send_pet(folder):
    pet_slice_no = 0
    for img in sorted(listdir(folder)):
        pet_slice = dict()
        with open(path.join(folder, img), "rb") as image_file:
            encoded_string = base64.b64encode(
                image_file.read()).decode('utf-8')
            pet_slice['slice_no'] = pet_slice_no
            pet_slice['data'] = encoded_string

            #socketio.emit(PET, json.dumps(pet_slice))
            print(json.dumps(pet_slice))
        pet_slice_no += 1

    pet_img_upload = dict()
    pet_img_upload['id'] = "PET_IMG_UPLOAD"
    pet_img_upload['data'] = dict()
    pet_img_upload['data']['total_slice_number'] = len(listdir(folder))
    pet_img_upload['data']['uploaded'] = True

    emit(pet_img_upload)

mri_to_pet_conversion()
