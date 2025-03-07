import queue
import sys
from preprocessing_functions import get_grayscale, removeLines, remove_noise, adaptiveGaussianThresholding, erode

PREPROCESSING_STEPS = {
    "grayscale": get_grayscale,
    "remove_lines": removeLines,
    "remove_noise": remove_noise,
    "adaptive_gaussian_thresholding": adaptiveGaussianThresholding,
    "erode": erode
}


def processing_pipeline(img, queue=None): # Default parameter list will be treated as global
    """
    Takes an image and passes the image through a series of pre-processing steps

    Arguments:
    ___
    A .png or .jpg image

    Returns:
    ___
    A preprocessed image
    
    """
    new_image = img.copy()
    if queue is None:
        queue = ["grayscale","remove_lines","remove_noise","adaptive_gaussian_thresholding","erode"]
    
    grayscale_present = False
    for str1 in queue:
        if str1 == "grayscale":
            grayscale_present = True
        elif str1 == "adaptive_gaussian_thresholding":
            if not grayscale_present:
                sys.exit("[grayscale] must occur before [adaptive_gaussian_thresholding].")
    # If [grayscale] is before [adaptive_gaussian_thresholding] it will error out
    while len(queue) > 0:
        preprocessing_number = queue.pop(0)

        # Corresponds to preprocessing function
        preprocessing_function = PREPROCESSING_STEPS.get(preprocessing_number)
        new_image = preprocessing_function(new_image)

    return new_image
    