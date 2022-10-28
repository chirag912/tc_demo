import re
import numpy as np
import pytesseract
import cv2 as cv
import datetime

# Specifying the path
#pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe' 

#Function to Finds Departing Dates
def date(textlist):
  date = []
  for text in textlist:
    if re.search(r'(\w{3},\s+\w{3}\s+\d{1,2},\s+\d{2}:\d{2}|\w{3}\s+\w{3}\s+\d{1,2},\s+\d{4}|\w{3},\s+\w{3}\s+\d{1,2},\s+\d{4}|\w{3},\s+\w{3}\s+\d{1,2}|\d{2}\s+\w{0,9}\s+\d{4})',text):
      clr = text.replace('Thursday ','').replace('Friday ','')
      date.append(clr)
  return date

#Extracting the Info
def extract_ticket(filename):
    image = cv.imread(filename,0)
    #Extracting From Tesseract Entities
    Extracted_text = pytesseract.image_to_string(image,lang = 'eng',config = '--psm 4 --oem 3 -c tesseract_char_whitelist=ABCDEFG0123456789')
    text_output = open('output.txt', 'w', encoding='utf-8')
    text_output.write(Extracted_text)
    text_output.close()

    return Extracted_text

# Function to read Entities from the extracted Information
def ticket_read_data(text):
    text1 = []
    DOT = None
    DOR = None
    COT = None
    lines = text.split('\n')
    for lin in lines:
        s = lin.strip()
        s = lin.replace('\n','')
        s = s.rstrip()
        s = s.lstrip()
        text1.append(s)

    text1 = list(filter(None, text1))
    #print(text1)
    # Getting Dates
    Dates = date(text1)

    '''
    # Days List to Compare
    Day = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT','SUN','Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    # To Get Final Dates
    FDates = []
    # Looping to Get Final Dates
    for D in Day:
        for i in Dates:
            if re.search(D, i):
                FDates.append(i)
    
    '''

    # Date of Travel
    try:
        try:
            dot = Dates[0]
            d = re.search(r'(\d{2})',dot).group()
            m = re.search(r"Jan|JAN|Feb|FEB|Mar|MAR|Apr|APR|May|MAY|Jun|JUN|Jul|JUL|Aug|AUG|Sep|SEP|Oct|OCT|Nov|NOV|Dec|DEC",dot).group()
            m = m.replace("Jan", '01').replace("JAN", '01').replace("Feb", '02').replace("FEB", '02').replace("Mar", '03').replace("MAR", '03')
            m = m.replace("Apr", '04').replace("APR", '04').replace("May", '05').replace("MAY", '05').replace("Jun", '06').replace("JUN", '06')
            m = m.replace("July", "07").replace("Jul", "07").replace("JUL", "07").replace("Aug", '08').replace("AUG", '08')
            m = m.replace("Sep", '09').replace("SEP", '09').replace("Oct", '10').replace("OCT", '10')
            m = m.replace("Nov", "11").replace("NOV", "11").replace("Dec", "12").replace("DEC", "12")
            try:
               y = re.search(r'\d{4}',dot).group()
               DATE = d + "/" + m + "/" + y
               DOT = DATE
            except AttributeError:
                currentDate = datetime.date.today()
                DATE = d + "/" + m + "/" + str(currentDate.year)
                DOT = DATE
        except IndexError:
            DOT = None
    except AttributeError:
        DOT = None
    # Date of Return
    try:
        try:
            dor = Dates[-1]
            # Checking if date of travel & date of return is extracted same
            if dot == dor:
                DOR = None
            else:
                d = re.search(r'(\d{2})',dor).group()
                m = re.search(r"Jan|JAN|Feb|FEB|Mar|MAR|Apr|APR|May|MAY|Jun|JUN|Jul|JUL|Aug|AUG|Sep|SEP|Oct|OCT|Nov|NOV|Dec|DEC",dor).group()
                m = m.replace("Jan", '01').replace("JAN", '01').replace("Feb", '02').replace("FEB", '02').replace("Mar", '03').replace("MAR", '03')
                m = m.replace("Apr", '04').replace("APR", '04').replace("May", '05').replace("MAY", '05').replace("Jun", '06').replace("JUN", '06')
                m = m.replace("July", "07").replace("Jul", "07").replace("JUL", "07").replace("Aug", '08').replace("AUG", '08')
                m = m.replace("Sep", '09').replace("SEP", '09').replace("Oct", '10').replace("OCT", '10')
                m = m.replace("Nov", "11").replace("NOV", "11").replace("Dec", "12").replace("DEC", "12")
                try:
                   y = re.search(r'\d{4}',dor).group()
                   DATE = d + "/" + m + "/" + y
                   DOR = DATE
                except AttributeError:
                    currentDate = datetime.date.today()
                    DATE = d + "/" + m + "/" + str(currentDate.year)
                    DOR = DATE
        except IndexError:
            DOR = None
    except AttributeError:
        DOR = None

    # City of Travel
    

    data = {}
    data['ID Type'] = "Ticket"
    data['Date of Travel'] = DOT
    data['Date of Return'] = DOR
    return  data