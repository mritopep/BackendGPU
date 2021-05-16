import numpy as np
import nibabel
from scipy import ndimage
import sys, getopt

if len(sys.argv) < 3:
	print("Usage : denoise.py -i <input_img_path> [-o <output_dir_name>] [-s denoise_strength]")
	exit()

path = ""
denoise_strength = 3
img_file = ""

opts, _ = getopt.getopt(sys.argv[1:], "i:o:s:") 
for inp, arg in opts :
	if inp == '-i' : img_file = arg
	elif inp == '-o' : path = arg
	elif inp == "-s" : denoise_strength = int(arg)
	
if img_file == "" : 
	print("Usage : denoise.py -i <input_img_path> [-o <output_dir_name>] [-s denoise_strength]")
	exit()

data = np.asarray(nibabel.load(img_file).dataobj)
print(data.shape)
data_filtered = np.zeros(data.shape)
slices = data.shape[2]

for i in range(slices):
    data_filtered[:,:,i,0] = ndimage.median_filter(data[:,:,i,0], denoise_strength)

new_image = nibabel.Nifti1Image(data_filtered, affine=np.eye(4))
nibabel.save(new_image, path)
