import re
import pytesseract
from PIL import Image

# Specifying the path
#pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe' 

# Function to Extract Information from PAN Using Tesseract.
def extract_pan(filename):

    #Extracting From Tesseract Entities
    #Extracted_text = pytesseract.image_to_string(Image.open(filename), lang = 'eng',config = '--psm 4 --oem 3 -c tesseract_char_whitelist=ABCDEFG0123456789')
    Extracted_text = pytesseract.image_to_string(Image.open(filename))
    text_output = open('output.txt', 'w', encoding='utf-8')
    text_output.write(Extracted_text)
    text_output.close()

    return Extracted_text

# Function to Check the Number of Space in a Sentence
def check_space(string):
    count_s = 0
    for i in range(0, len(string)):
        if string[i] == " ":
            count_s += 1
    return count_s

# Function to Find a particular Word in a Sentence.
def findword(textlist, wordstring):
    lineno = -1
    for wordline in textlist:
        xx = wordline.split( )
        if ([w for w in xx if re.search(wordstring, w)]):
            lineno = textlist.index(wordline)
            textlist = textlist[lineno+1:]
            return textlist
    return textlist


# Function to read Entities from the extracted Information
def pan_read_data(text):
    name = None
    fname = None
    dob = None
    pan = None
    panline = []
    text0 = []
    text1 = []
    text2 = []
    lineno = 0
    lines = text.split('\n')
    for lin in lines:
        s = lin.strip()
        s = lin.replace('\n','')
        s = s.rstrip()
        s = s.lstrip()
        text1.append(s)
    text1 = list(filter(None, text1))
    lineno = 0

    for wordline in text1:
            xx = wordline.split('\n')
            if ([w for w in xx if re.search('(INCOMETAXDEPARWENT|INCOME|TAX|GOW|GOVT|GOVERNMENT|OVERNMENT|VERNMENT|DEPARTMENT|EPARTMENT|PARTMENT|ARTMENT|INDIA|NDIA)$', w)]):
                text1 = list(text1)
                lineno = text1.index(wordline)
                break
    text0 = text1[lineno+1:]
    
    #Getting Names
    Names = []
    for words in text0:
        if check_space(words) == 2 and words.isupper():
            Names.append(words)

    try:
        # Cleaning first names
        name = Names[0]
        name = name.rstrip()
        name = name.lstrip()
        name = name.replace("8", "B")
        name = name.replace("0", "D")
        name = name.replace("6", "G")
        name = name.replace("1", "I")
        name = name.replace("\"","")
        name = re.sub('[^a-zA-Z] +', ' ', name)

    # Cleaning Father's name
        if len(Names) >= 2:
            fname = Names[1]
            fname = fname.rstrip()
            fname = fname.lstrip()
            fname = fname.replace("8", "S")
            fname = fname.replace("0", "O")
            fname = fname.replace("6", "G")
            fname = fname.replace("1", "I")
            fname = fname.replace("!", "I")
            fname = re.sub('[^a-zA-Z] +', ' ', fname)
        else:
            fname = None

    # Cleaning DOB
        dob = re.search(r'(\d+/\d+/\d+)',text).group()

    # Cleaning PAN Card details
        pantext0 = findword(text1, '(Pormanam|Number|umber|Account|ccount|count|Permanent|ermanent|manent|wumm)$')
        panline = pantext0[0]
        pan = panline.rstrip()
        pan = pan.lstrip()
        pan = pan.replace(" ", "")
        pan = pan.replace("\"", "")
        pan = pan.replace(";", "")
        pan = pan.replace("%", "L")
    except:
        pass


    data = {}
    data['Name'] = name
    data['Father Name'] = fname
    data['Date of Birth'] = dob
    data['PAN'] = pan
    data['ID Type'] = "PAN"
    return data

