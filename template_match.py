#Importing the required library
import numpy as np
import cv2 as cv

# List of Template Files.
templates = []
threshold = 0.50
# Max values of our result
acc = []

# Function to Match the Templates.
def doTemplateMatch(temp_name,base_img):
    # Looping for getting images
    if temp_name == 'aadhaar' or temp_name == 'pan':
        for i in range(2):
            templates.append(cv.imread("templates/image - {}_temp{}.jpg".format(temp_name,i), 0))

        # Reading n resizing.
        img = cv.imread('{}'.format(base_img), 0)
        resize_img = cv.resize(img, (700,500), interpolation=cv.INTER_AREA)
        
        # Looping for Each Template
        for template in templates: 
            res = cv.matchTemplate(resize_img, template, cv.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
            if max_val >= threshold:
                acc.append(max_val)
    '''
    elif temp_name == 'passport':
        for i in range(1):
            templates.append(cv.imread("templates/image - {}_temp{}.jpg".format(temp_name,i), 0))

        # Reading n resizing.
        img = cv.imread('{}'.format(base_img), 0)
        resize_img = cv.resize(img, (700,500), interpolation=cv.INTER_AREA)
        
        # Looping for Each Template
        for template in templates: 
            res = cv.matchTemplate(resize_img, template, cv.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
            if max_val >= threshold:
                acc.append(max_val)
    '''
    # Accuracy for both the templates
    return acc