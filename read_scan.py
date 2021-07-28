import nibabel as nib
import numpy as np
from skimage import exposure
from scipy import ndimage


def read_nifti_file(filepath):
    """Read and load volume"""
    # Read file
    scan = nib.load(filepath)
    # Get raw data
    scan = scan.get_fdata()
    return scan

def gamma_correction(volume):
    equalized_data = exposure.equalize_hist(volume)
    vmin, vmax = np.percentile(equalized_data, q=(0.5, 99.5))
    clipped_data = exposure.rescale_intensity(equalized_data,in_range=(vmin, vmax),out_range=np.float32)
    return clipped_data


def resize_volume(img):
    """Resize across z-axis"""
    # Set the desired depth
    desired_depth = 64
    desired_width = 256
    desired_height = 256
    # Get current depth
    current_depth = img.shape[-1]
    current_width = img.shape[0]
    current_height = img.shape[1]
    # Compute depth factor
    depth = current_depth / desired_depth
    width = current_width / desired_width
    height = current_height / desired_height
    depth_factor = 1 / depth
    width_factor = 1 / width
    height_factor = 1 / height
    # Rotate
    img = ndimage.rotate(img, 90, reshape=False)
    # Resize across z-axis
    img = ndimage.zoom(img, (width_factor, height_factor, depth_factor), order=1)
    return img


def process_scan(path):
    """Read and resize volume"""
    # Read scan
    volume = read_nifti_file(path)
    # Normalize
    # volume = normalize(volume)
    volume = gamma_correction(volume)
    # Resize width, height and depth
    volume = resize_volume(volume)
    return volume


def load_processed_img(path):
    img = process_scan(path)
    img = np.expand_dims(img, axis=0)
    return img