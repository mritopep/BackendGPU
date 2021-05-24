from keras.models import load_model
import nibabel as nib
from numpy import load, zeros, copy, arange, eye
from os import path, rename
from statuses import BIAS_CORRECTION, DENOISE, SKULL_STRIP
import cv2
import os
from os import listdir
from os import system as run
import numpy as np
from med2img.med2img import convert
from matplotlib import pyplot as plt
import shutil
import gzip
from soft.src.skull import SkullStripper
from scipy import ndimage
import SimpleITK as sitk
import time

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


THIS_FOLDER = path.dirname(path.abspath(__file__))


def normalize(x):
    return np.array((x - np.min(x)) / (np.max(x) - np.min(x)))


def img_to_nii(img):
    res = np.zeros(img.shape[:-1])

    for i in range(img.shape[0]):
        res[i] = cv2.flip(cv2.cvtColor(
            np.float32(img[i]), cv2.COLOR_BGR2GRAY), 0)

    return nib.Nifti1Image(res.T, affine=None)


def load_test():
    processed_data = path.join(
        THIS_FOLDER, 'model/gamma_corrected_test_data.npz')
    dataset = load_real_samples(processed_data)
    print(bcolors.UNDERLINE + "Input :",
          dataset[0].shape, "Output :", dataset[1].shape, bcolors.ENDC)
    image_shape = dataset[0].shape[1:]
    [X1, X2] = dataset
    return [X1, X2]


def model():
    g_model_file = path.join(THIS_FOLDER, 'model/g_model_ep_000035.h5')
    generator = load_model(g_model_file)
    return generator


def load_real_samples(filename):
    data = load(filename)
    X1, X2 = data['arr_0'], data['arr_1']
    X1 = (X1 - 127.5) / 127.5
    X2 = (X2 - 127.5) / 127.5
    return [X1, X2]


def gamma_correction(image):
    gamma = 0.15
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    image = cv2.LUT(image, table).astype(np.uint8)
    return image


def read_nifti(file, send_mri=None):
    
    folder = "./input/img"

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    convert(file, "./input/img/")
    files = sorted(listdir(folder))

    if send_mri : send_mri(folder)

    images = []

    # input/img/img-slice000.png

    print(bcolors.BOLD, len(files), bcolors.ENDC)

    for i in range(len(files)):
        data = cv2.imread(folder + '/' + files[i])
        print(data.shape)
        data = gamma_correction(data)
        padded_input = pad_2d(data, 256, 256)
        images.append(padded_input)

    images = np.asarray(images)
    return images


def upzip_gz(input, output):
    with gzip.open(input, 'rb') as f_in:
        with open(output, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


# def skull_strip(input_image):
#     begin = time.time() 
#     print("\nSKULL STRIPPING\n")
#     skull_stripper = SkullStripper(input_image, "input/temp/skull_strip", False, False)
#     skull_stripper.strip_skull()
#     upzip_gz("input/temp/skull_strip/mri_masked.nii.gz","input/temp/skull_strip/mri_sk.nii")
#     end = time.time() 
#     print("Total time taken :", (end - begin)//60 ,"min.", (end - begin)%60 , "s")

    
def denoise(input_image, output_image):
    begin = time.time() 
    print("\nDENOISING\n")
    denoise_strength = 3
    data = np.asarray(nib.load(input_image).dataobj)
    data_filtered = np.zeros(data.shape)
    slices = data.shape[2]

    if len(data.shape) == 4:
        for i in range(slices):
            data_filtered[:,:,i,0] = ndimage.median_filter(data[:,:,i,0], denoise_strength)
    else :
        for i in range(slices):
            data_filtered[:,:,i] = ndimage.median_filter(data[:,:,i], denoise_strength)
            
    new_image = nib.Nifti1Image(data_filtered, affine=np.eye(4))
    nib.save(new_image, output_image)
    end = time.time() 
    print(bcolors.UNDERLINE + "Total time taken :", (end - begin)//60 ,"min.", (end - begin)%60 , "s" + bcolors.ENDC)

def bias_correction(input_image, output_image):
    print("\nBIAS CORRECTION\n")
    begin = time.time()
    inputImage = sitk.ReadImage(input_image, sitk.sitkFloat32)
    corrector = sitk.N4BiasFieldCorrectionImageFilter()
    maskImage = sitk.OtsuThreshold(inputImage, 0, 1, 200)
    numberFittingLevels = 4
    output = corrector.Execute(inputImage, maskImage)
    log_bias_field = corrector.GetLogBiasFieldAsImage(inputImage)
    output = inputImage / sitk.Exp( log_bias_field )
    sitk.WriteImage(output, output_image)
    end = time.time() 
    print(bcolors.UNDERLINE + "Total time taken :", (end - begin)//60 ,"min.", (end - begin)%60 , "s" + bcolors.ENDC)

def skull_strip(input_image):
    print("\nSKULL STRIPPING\n")
    log_name = "SKULL_STRIPPING"
    SKULL_STRIP = "input/temp/skull_strip"
    run(f"bash shell_scripts/skull_strip.sh {input_image} {SKULL_STRIP} {log_name}")
    upzip_gz(f"{SKULL_STRIP}/mri_masked.nii.gz",f"{SKULL_STRIP}/mri_sk.nii")

def preprocess(input, Skull_Strip=False, Denoise=False, Bias_Correction=False, emit = None, status = None):
    print("\n-------------------MRI PREPROCESS STARTED--------------------\n")
    if(Denoise):
        denoise(input, "input/temp/denoise/mri")
        input = "input/temp/denoise/mri.nii"
        if emit : 
            status['data'][DENOISE] = True
            emit(status)

    if(Skull_Strip):
        skull_strip(input)
        input = "input/temp/skull_strip/mri_sk.nii"
        if emit : 
            status['data'][SKULL_STRIP] = True
            emit(status)

    if(Bias_Correction):
        bias_correction(input, "input/temp/bias_cor/mri.nii")
        input = "input/temp/bias_cor/mri.nii"
        if emit : 
            status['data'][BIAS_CORRECTION] = True
            emit(status)

    shutil.copyfile(input, "input/temp/output/mri.nii")
    print("\nTemp mri image: " + "input/temp/output/mri.nii")
    print("\n-------------------MRI PREPROCESS COMPELETED--------------------\n")



# def intensity_normalization(input_image, output_image):
#     print("\nDENOISING\n")
#     # print("\ninput image: "+ input_image)
#     # print("\noutput image: "+ output_image)
#     log_name = "DENOISING"
#     run(
#         f"bash {SHELL}/denoise.sh {input_image} {output_image} {log_name}")
#     return exception_handle(log_name)


# def skull_strip(input_image):
#     scan = input_image.split("/")[-1][:-4]
#     print("\nSKULL STRIPPING\n")
#     # print("\ninput image: "+ input_image)
#     # print("\noutput image: "+ f"{SKULL_STRIP}/{scan}_sk.nii")
#     log_name = "SKULL_STRIPPING"
#     run(
#         f"bash {SHELL}/skull_strip.sh {input_image} {SKULL_STRIP} {log_name}")
#     upzip_gz(f"{SKULL_STRIP}/{scan}_masked.nii.gz",
#              f"{SKULL_STRIP}/{scan}_sk.nii")
#     return exception_handle(log_name)


# def bias_correction(input_image, output_image):
#     print("\nBIAS CORRECTION\n")
#     # print("\ninput image: "+ input_image)
#     # print("\noutput image: "+ output_image)
#     log_name = "BIAS_CORRECTION"
#     run(f"bash {SHELL}/bias.sh {input_image} {output_image} {log_name}")
#     return exception_handle(log_name)


# def preprocess(input, Skull_Strip=True, Denoise=True, Bais_Correction=True):
#     print("\n-------------------MRI PREPROCESS STARTED--------------------\n")
#     if(Denoise):
#         if(intensity_normalization(input, f"{DENOISE}/mri")):
#             input = f"{DENOISE}/mri.nii"
#         else:
#             return False
#     if(Skull_Strip):
#         if(skull_strip(input)):
#             input = f"{SKULL_STRIP}/mri_sk.nii"
#         else:
#             return False
#     if(Bais_Correction):
#         if(bias_correction(input, f"{BAIS_COR}/mri.nii")):
#             input = f"{BAIS_COR}/mri.nii"
#         else:
#             return False
#     shutil.copyfile(input, f"{TEMP_OUTPUT}/mri.nii")
#     print("\nTemp mri image: " + f"{TEMP_OUTPUT}/mri.nii")
#     print("\n-------------------MRI PREPROCESS COMPELETED--------------------\n")
#     return True


def pad_2d(data, r, c):
    m, n, other = data.shape
    res = np.zeros((r, c, other))
    res[(r - m) // 2: (r - m) // 2 + m, (c - n) // 2: (c - n) // 2 + n, :] = data
    return res


def crop_2d(data, r, c):
    m, n = data.shape
    return data[(m - r) // 2: (m - r) // 2 + r, (n - c) // 2: (n - c) // 2+c]