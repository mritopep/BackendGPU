from keras.models import load_model
import nibabel as nib
from numpy import load, zeros, copy, arange, eye
from os import path
import cv2
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

from model_util import *


class Mri2Pet:

    def __init__(self, load_test_data=False):
        self.model = model()
        if load_test_data:
            self.test_data = load_test()
        self.test_data = None
        self.img = None

    def test(self, n=245, m=50):
        input_images = self.test_data[0][n: n+m]
        output_img = self.predict(input_images)
        output_nii = img_to_nii(output_img)

        nib.save(output_nii, path.join(
            THIS_FOLDER, 'output/nii/output.nii.gz'))

    def process(self, file, Skull_Strip, Denoise, Bias_Correction, emit, status):
        print(bcolors.OKBLUE + "Processing Data..." + bcolors.ENDC)
        preprocess(file, Skull_Strip=Skull_Strip, Denoise=Denoise, Bias_Correction=Bias_Correction ,emit=emit, status=status)
        self.img = read_nifti("input/temp/output/mri.nii")
        print(bcolors.OKBLUE + "Processing complete" + bcolors.ENDC)

    def save(self):
        print(bcolors.OKBLUE + "Saving .nii file of result..." + bcolors.ENDC)
        output_nii = img_to_nii(self.img)
        nib.save(output_nii, path.join(THIS_FOLDER, 'output/nii/pet.nii.gz'))
        print(bcolors.OKBLUE + "Completed" + bcolors.ENDC)

    def generate(self):
        print(bcolors.OKBLUE + "Generating Pet..." + bcolors.ENDC)
        self.img = (self.img - 127.5) / 127.5
        fake_images = zeros(self.img.shape)
        slice_no = 1

        for i in range(len(self.img)):
            fake_images[i] = self.model.predict(self.img[i:i+1])
            print("Slice number :", slice_no, "completed")
            slice_no += 1

        predicted_imgs = copy(fake_images)
        predicted_data = path.join(THIS_FOLDER, 'output', 'img')

        print(bcolors.OKCYAN + "Result shape :",
              predicted_imgs.shape, bcolors.ENDC)

        for i in range(len(self.img)):
            plt.imsave(f"{predicted_data}/{i}.png",
                       normalize(predicted_imgs[i]), cmap=plt.cm.Greys_r)

        self.img = predicted_imgs
        print(bcolors.OKBLUE + "Pet Generation complete" + bcolors.ENDC)
