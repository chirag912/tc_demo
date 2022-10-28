import re
import numpy as np
import pytesseract
import cv2 as cv

# Specifying the path
#pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe' 

#User Defined Function - To Resize
def rescaleFrame(frame, scale=3.0):
    width = int(frame.shape[1] / scale)
    height = int(frame.shape[0] / scale)

    dimensions = (width,height)

    return cv.resize(frame, dimensions, interpolation=cv.INTER_AREA)


# Function to Find a particular Word in a Sentence.
def findword(textlist, wordlist):
  for text in textlist:
    for word in wordlist:
      if re.search(word, text):
        return text


# Function to get the address as address are in two different lines
def twolines(textlist, wordlist):
  ad = []
  li = iter(textlist)
  for text in li:
    for word in wordlist:
      if re.search(word, text):
        ad.append(text)
        ad.append(next(li))
        return ad

#Function to find first digit [for Passport]
def firstDigit(n):
  try:
    n = int(n)
    while n >= 10:
      n = n / 10;
  except ValueError as err:
    return 10    
  return int(n)

#Function to get the dates 
def date(textlist):
  date = []
  for text in textlist:
    if re.search(r'(\d+/\d+/\d+|\d+.\d+.\d+)',text):
      date.append(text)
  return date

#Function to get Next iter based on previous Entities
def nextentities(textlist,skiplist):
  li = iter(textlist)
  for text in li:
    for skip in skiplist:
      if re.search(skip, text):
        return next(li)

#Extracting the Info
def extract_annexure(filename):
    image = cv.imread(filename,0)
    if image.shape[0:2] >= (4000, 3000):
        resized_image = rescaleFrame(image)
        #Extracting From Tesseract Entities
        Extracted_text = pytesseract.image_to_string(resized_image,lang = 'eng',config = '--psm 4 --oem 3 -c tesseract_char_whitelist=ABCDEFG0123456789')
        text_output = open('output.txt', 'w', encoding='utf-8')
        text_output.write(Extracted_text)
        text_output.close()
    else:
        #Extracting From Tesseract Entities
        Extracted_text = pytesseract.image_to_string(image,lang = 'eng',config = '--psm 4 --oem 3 -c tesseract_char_whitelist=ABCDEFG0123456789')
        text_output = open('output.txt', 'w', encoding='utf-8')
        text_output.write(Extracted_text)
        text_output.close()

    return Extracted_text

# Function to read Entities from the extracted Information
def annexure_read_data(text):
    CHN = None
    CN = None
    ADD = None
    PN = None
    MN = None
    EM = None
    DOB = None
    DOI = None
    DOE = None
    MON = None
    PAN = None
    CT = None
    CAT = None
    TT = None
    TD = None
    AM = None
    FFMCN = None
    FFMCAN = None
    AMT = None
    REF = None
    text0 = []
    text1 = []
    lines = text.split('\n')
    for lin in lines:
        s = lin.strip()
        s = lin.replace('\n','')
        s = s.rstrip()
        s = s.lstrip()
        text1.append(s)

    if 'btq' in text.lower():
        TT = "BTQ"
    elif 'business' in text.lower():
        TT = 'BUSINESS'
    else:
        TT = "BT"
    
    text1 = list(filter(None, text1))
    #print(text1)
    #Getting Card Holder Name
    chn =  findword(text1, ['Card Holder Name','Card Holder','Card Holder Nam','card Holder Name'])

    #Getting Card Number
    cn = twolines(text1, ['Card Number','Card Num','card Number'])

    #Getting the Address
    add = twolines(text1, ['Address','address'])

    #Getting Passport Number
    pn = findword(text1, ['Passport','passport','passpor','passpo'])

    #Getting Mobile Number
    mn = findword(text1, ['Mobile','Moblie'])

    #Getting Email id
    em = findword(text1, ['LEmall','Email','email'])

    #Getting the dates like dob, doi, doe
    dates = date(text1[14:21])

    #Cleaning Dates
    for d in dates:
        if d.startswith("P"):
            dates.remove(d)

    for d in dates:
        if d.startswith("M"):
            dates.remove(d)
    #Getting Mother Name
    mon = findword(text1,['Mother','mother'])

    #Getting PAN Number
    pan = findword(text1,['Customer','Customer Pan Card'])

    #Getting Currency Type
    ct = findword(text1,['Currency','currency'])

    #Getting Card Type
    cat = nextentities(text1,['Currency','currency'])

    #Getting Travel Date
    td = findword(text1,['Travel Date'])

    #Getting Amount
    am = findword(text1,['Amount','amount'])

    #Getting FFMCName
    ffmcn = findword(text1, ['FFMCName','FFMC Name','Account','Account Name'])

    #Getting FFMC Account No.
    ffmcan = findword(text1, ['FFMC Account No','AccountNo','Account No'])

    #Getting Amount
    amt = nextentities(text1, ['FFMC Account No','AccountNo','Account No'])

    #Getting Reference No or IFSC No
    ref = findword(text1, ['Reference','IFSC'])

    try:
        # Cleaning Card Holder Name
        CHN = re.findall(r'\b[A-Z]+(?:\s+[A-Z]+)*\b', chn)[0]

        # Cleaning Card Number
        cN = re.findall(r'\d+',cn[0])
        card_number = ''
        #Looping when there is space between the card numbers.
        for word in cN:
            if len(word) == 4 and word.isdigit():
                card_number = card_number  + word + ' '
                CN = card_number
            else:
                CN = cN[0]

        # Cleaning the Address
        ad = add[0]
        ad = ad.replace('Address ','').replace(':','').replace('-','').replace('‘','').replace('"| ','').replace('address','')
        ad = ad.lstrip()
        ad = ad.rstrip()
        #Looping if Address is of two line
        if len(cn) == 2 and cn[1] != add[0]:
            ADD = cn[1] + ' ' + ad
            ADD = ADD.replace('|','').replace(')','I').replace('au','')
            ADD = ADD.lstrip()
            ADD = ADD.rstrip()
        elif len(add) == 2 and add[1].startswith('Passport'):
            ADD = ad
        else:
            ADD = ad + ' ' + add[1]

        # Cleaning the Passport Number
        pn = pn.replace("Passport No","").replace("[.",'').replace("_",'').replace('|','').replace('=','').replace("O",'0').replace(".",'').replace(" ",'').replace("eriaks-",'')
        pn = pn.replace('“[','').replace('passportNo','').replace(':','').replace('ee','').replace('ia','')
        pn = pn.lstrip()
        pn = pn.rstrip()
        #PN = pn

        #Looping to Change the First digit to Alpha numberic
        if firstDigit(pn) == 2 or firstDigit(pn) == 7:
            nnn = re.sub(r'\d',r'Z', pn, count = 1)
            PN = nnn
        else:
            PN = pn

        # Cleaning Mobile Number
        mn = re.findall(r'\d+',mn)
        MN = mn[0]

        #Cleaning the Email id.
        email = re.findall("[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", em.lower())
        try:
            EM = email[0].upper()
        except IndexError:
            EM = [j.group() for j in (re.search("[A-Za-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", i) for i in text1) if j][0]

        #Cleaning DOB
        dob = re.search(r'(\d+/\d+/\d+|\d+.\d+.\d+)',dates[0].replace('0.0.8','')).group()
        DOB = dob

        #Cleaning DOI
        doi = re.search(r'(\d+/\d+/\d+|\d+.\d+.\d+)',dates[1].replace('0.0.1 ','')).group()
        DOI = doi

        #Cleaning DOE
        doe = re.search(r'(\d+/\d+/\d+|\d+.\d+.\d+)',dates[2].replace('mone C13','')).group()
        DOE = doe

        #Cleaning Mother Name
        MON = re.findall(r'\b[A-Z]+(?:\s+[A-Z]+)*\b', mon)[0]

        #Cleaning PAN Card Number
        try:
            pan = pan.replace('(Customer Pan Card)','').replace('BTQ','').replace('jee','').replace('   ','')
            #pan.lstrip()
            PAN = pan
        except AttributeError:
            PAN = None

        #Cleaning Currency Type
        ct = ct.upper()
        CT = re.findall(r'\b[A-Z]+(?:\s+[A-Z]+)*\b', ct.replace('CURRENCY TYPE ','').replace('CURRENCY ','').replace('ES ',''))[0]

        #Cleaning Card Type
        CAT = re.findall(r'\b[A-Z]+(?:\s+[A-Z]+)*\b', cat)[0]

        #Cleaning Travel Date
        try:
            td = re.search(r'(\d+/\d+/\d+|\d+.\d+.\d+)',td).group()
            TD = td
        except TypeError:
            TD = None

        #Cleaning Amount
        am = am.upper()
        am = re.findall(r'\b[A-Z0-9]+(?:\s+[(A-Z0-9)]+)*\b', am.replace('AMOUNT ','').replace('USB','USD'))[0]
        am = am.replace('(', '- ')
        AM = am

        #Cleaning FFMCName
        ffmcn = ffmcn.replace('Account Name: ','').replace("Account Name ","").replace('FFMCName ','').replace(".",'').replace(": ",'').replace(':- ','').replace('_','')
        ffmcn = ffmcn.lstrip()
        ffmcn = ffmcn.rstrip()
        FFMCN = ffmcn

        #Cleaning FFMC Account No
        ffmcan = re.findall(r'\d+',ffmcan)[0]
        #ffmcan = ffmcan.lstrip()
        #ffmcan = ffmcan.rstrip()
        FFMCAN = ffmcan

        #Cleaning the Amount
        AMT = re.findall(r'\d+,\d+|\d+',amt.replace(',',''))[0]

        #Cleaning the Reference No or IFSC No
        ref = ref.replace('Reference / UTR No:','').replace("Reference/ IFSC No.","").replace('Reference No ','').replace(".",'').replace(": ",'').replace(':- ','').replace('=','')
        ref = ref.lstrip()
        ref = ref.rstrip()

        if len(ref) != 0:
            REF = ref
        else:
            REF = REF


    except:
        pass

    data = {}
    data['SOF'] = 'Self'
    data['Card Holder Name'] = CHN
    data['Card Number'] = CN
    data['Address'] = ADD
    data['Passport Number'] = PN
    data['Mobile Number'] = MN
    data['Email ID'] = EM
    data['D.O.B'] = DOB
    data['D.O.I'] = DOI
    data['D.O.E'] = DOE
    data['Mother Name'] = MON
    data['Pan No'] = PAN
    data['Currency Type'] = CT
    data['Card Type / Type'] = CAT
    data['Amount In Currency'] = AM
    data['Travel Type'] = TT
    data['Travel Date'] = TD
    data['FFMCName / Account Name'] = FFMCN
    data['FFMC Account No / Account No'] = FFMCAN
    data['Amount'] = AMT
    data['Reference No / IFSC No'] = REF
    data['ID Type'] = "Annexure"
    return data

