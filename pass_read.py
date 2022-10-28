import re
import pytesseract
import cv2 as cv
from PIL import Image

#User Defined Function - To Resize
def rescaleFrame(frame, scale=4.0):
    width = int(frame.shape[1] / scale)
    height = int(frame.shape[0] / scale)

    dimensions = (width,height)

    return cv.resize(frame, dimensions, interpolation=cv.INTER_AREA)

# Function to get the Entities on Different lines
def diff(textlist, wordlist):
  ad = []
  li = iter(textlist)
  for text in li:
    for word in wordlist:
      if re.search(word, text):
        ad.append(text)
        ad.append(next(li))
        return ad

#Function to get dates
def date(textlist):
  date = []
  for text in textlist:
    if re.search(r'(\d+/\d+/\d+)',text):
      date.append(text)
  return date

def extract_passport(filename):
    image = cv.imread(filename,0)
    if image.shape[0:2] >= (3000, 4000):
        resized_image = rescaleFrame(image)
        #Extracting From Tesseract Entities
        Extracted_text = pytesseract.image_to_string(resized_image,lang = 'eng',config = '--psm 4 --oem 3')
        text_output = open('output.txt', 'w', encoding='utf-8')
        text_output.write(Extracted_text)
        text_output.close()
    else:
        #Extracting From Tesseract Entities
        Extracted_text = pytesseract.image_to_string(image,lang = 'eng',config = '--psm 4 --oem 3')
        text_output = open('output.txt', 'w', encoding='utf-8')
        text_output.write(Extracted_text)
        text_output.close()

    return Extracted_text

def pass_read_data(text):
    PNO = None
    SUR = None
    NAME = None
    NATY = None
    SEX = None
    DOB = None
    POB = None
    POI = None
    DOI = None
    DOE = None
    COD = None
    FN = None
    MN = None
    SN = None
    text1 = []
    lines = text.split('\n')
    for lin in lines:
        s = lin.strip()
        s = lin.replace('\n','')
        s = s.rstrip()
        s = s.lstrip()
        text1.append(s)

    text1 = list(filter(None, text1))
    #print(text1)

    #Getting Sex Entities
    if 'm' in text.lower():
        SEX = "M"
    else:
        SEX = "F"

    #Getting Nationality
    if "indian" in text.lower():
        NATY = "INDIAN"
    else:
        NATY = None

    #Getting Passport No & Surname(as with surname we have passport number)
    pno = diff(text1,['Passport No','Pas sport','Surname'])
    sur = diff(text1,['Surname','surname'])

    #Getting Given Name.
    name = diff(text1,['Given','Given Name(s)'])

    #Getting Place of Birth
    pob = diff(text1,['Place of Birth'])

    #Getting Place of Issue
    poi = diff(text1,['Place of Issue'])

    #Getting Dates
    dates = date(text1)

    #Father Name
    fn = diff(text1,['Father', 'Name of Father'])

    #Mother Name
    mn = diff(text1,['Mother', 'Name of Mother'])

    #Spouse Name
    sn = diff(text1,['Spouse', 'Name of Spouse'])

    #Getting the Unique Code.
    cod = text1[-2:]

    try:
        #Cleaning Passport No.
        try:
            PNO = re.findall(r'[A-Z]{1}[0-9]{7}|[$]{1}[0-9]{7}',pno[1])[0]
            PNO = PNO.replace('$','S')
        except IndexError:
            PNO = re.findall(r'[A-Z]{1}[0-9]{7}|[$]{1}[0-9]{7}',pno[0])[0]
            PNO = PNO.replace('$','S')


        #Cleaning surname.
        sur = sur[1]
        SUR = sur

        #Cleaning Name
        Name = name[1]
        NAME = Name

        #Cleaning POB
        POB = pob[1]

        #Cleaning POI
        POI = poi[1]

        #Cleaning Father's Name
        FN = fn[1]

        #Cleaning Mother's Name
        MN = mn[1]

        #Cleaning Spouse's Name
        SN = sn[1]

        #Cleaning Dates
        dates = list(dates[0].split(" "))
        Dates = date(dates)
        if len(Dates) == 3:
            DOI = Dates[1]
            DOE = Dates[2]
        else:
            DOI = Dates[0]
            DOE = Dates[1]

        #Cleaning the barcode
        j = None
        k = None
        l = None
        m = None
        s1 = cod[0]
        #Cleaning if More then 45 Character in the String
        if len(cod[1]) == 45:
            for i in cod[1]:
                if i == 'I':
                    k = j
                j = i
                if i == k:
                    m = l
                l = i

            if m != None and k != None:
                if m.isdigit() and k.isdigit():
                    lis = list(cod[1])
                    p = lis.index(k)
                    del(lis[p])
                    s2 = "".join(lis)
                    s2 = s2.replace('$','S')
            #Final code        
            cod_f = s1 + s2

        else:
            cod_f = s1 + cod[1]

        COD = cod_f

    except:
        pass


    data = {}
    data['Passport No'] = PNO
    data['Surname'] = SUR
    data['Name'] = NAME
    data['Nationality'] = NATY
    data['Sex'] = SEX
    data['Date of Birth'] = DOB
    data['Place of Birth'] = POB
    data['Place of Issue'] = POI
    data['Date of Issue'] = DOI
    data['Date of Expiry'] = DOE
    data['Unique Code'] = COD
    data['Father Name'] = FN
    data['Mother Name'] = MN
    data['Spouse Name'] = SN
    data['ID Type'] = 'Passport'

    return data