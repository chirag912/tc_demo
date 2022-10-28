import re
import numpy as np
import pytesseract
import cv2 as cv

# Specifying the path
#pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe' 


# Extracting the Info
def extract_visa(filename):
    image = cv.imread(filename,0)
    #Extracting From Tesseract Entities
    Extracted_text = pytesseract.image_to_string(image,lang = 'eng',config = '--psm 4 --oem 3 -c tesseract_char_whitelist=ABCDEFG0123456789')
    text_output = open('output.txt', 'w', encoding='utf-8')
    text_output.write(Extracted_text)
    text_output.close()

    return Extracted_text

# Function to Find a particular Word in a Sentence.
def findword(textlist, wordlist):
  for text in textlist:
    for word in wordlist:
      if re.search(word, text):
        return text

# Function to read Entities from the extracted Information
def visa_read_data(text):
    text1 = []
    DOI = None
    DOE = None
    lines = text.split('\n')
    for lin in lines:
        s = lin.strip()
        s = lin.replace('\n','')
        s = s.rstrip()
        s = s.lstrip()
        text1.append(s)

    text1 = list(filter(None, text1))
    #print(text1)

    # Date of Issue
    doi = findword(text1, ['Date & Place Of Issue','Valid from'])

    # Expiry Date
    doe = findword(text1, ['Valid Until'])

    # Cleaning Date of Issue
    try:
        try:
            doi =re.search(r'(\d+/\d+/\d+|\d+.\d+.\d+|\d+-\d+-\d+)',doi).group()
            doi = doi.replace("-","/")
            DOI = doi
        except TypeError:
            DOT = None
    except AttributeError:
        DOT = None
    
    # Cleaning Expiry Date
    try:
        try:
            doe =re.search(r'(\d+/\d+/\d+|\d+.\d+.\d+|\d+-\d+-\d+)',doe).group()
            doe = doe.replace("-","/")
            DOE = doe
        except TypeError:
            DOE = None
    except AttributeError:
        DOE = None

    data = {}
    data['ID Type'] = "Visa"
    data['Date of Issue'] = DOI
    data['Date of Expiry'] = DOE
    return  data