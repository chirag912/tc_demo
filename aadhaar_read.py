import re
import pytesseract
from PIL import Image

# Specifying the path
#pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe' 

# Function to Extract Information from Aadhaar Using Tesseract.
def extract_aadhaar(filename):

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

# Function to Check the Number of CAP Letters in a Word / Sentence
def check_case(string):
    count_c = 0
    for i in string:
        if i.isupper():
            count_c += 1
    return count_c

# Function to Find a particular Word in a Sentence.
def findword(textlist, wordlist):
  ad = []
  li = iter(textlist)
  for text in li:
    for word in wordlist:
      if re.search(word, text):
        ad.append(text)
        ad.append(next(li))
        return ad

# Function to read Entities from the extracted Information
def adhaar_read_data(text):
    res=text.split()
    name = None
    dob = None
    adh = None
    sex = None
    farname = None
    text0 = []
    text1 = []
    lines = text.split('\n')
    for lin in lines:
        s = lin.strip()
        s = lin.replace('\n','')
        s = s.rstrip()
        s = s.lstrip()
        text1.append(s)

    if 'female' in text.lower():
        sex = "FEMALE"
    else:
        sex = "MALE"
    
    text1 = list(filter(None, text1))
    text0 = text1[:]
    #print(text0)
    #print(res)

    # Getting first names
    Names = []
    for words in text0:
        if check_space(words) == 2 and check_case(words) == 3:
            Names.append(words)  

    # Getting Father names ^[^.]
    Father_names = findword(text0,['Father','father','Father : '])

    #Getting Year of birth
    Years = []
    for words in text0:
        if "Year" in words:
            Years.append(words)

    #Getting First number for the date if date is not properly fetched
    fno = ''
    for words in text0:
        if "DOB" in words:
            fno = re.search(r'(\d+)(?!.*\d)',words).group()


    # Getting Adhaar number details
    aadhar_number = ''
    for word in res:
        if len(word) == 4 and word.isdigit():
            aadhar_number=aadhar_number  + word + ' '

    try:
        # Cleaning first names
        name = Names[0]
        name = name.rstrip()
        name = name.lstrip()
        name = name.replace("8", "B")
        name = name.replace("0", "D")
        name = name.replace("6", "G")
        name = name.replace("1", "I")
        name = re.sub('[^a-zA-Z] +', ' ', name)

        try:
            Father = ''
            for words in Father_names:
                if words.startswith("Father"):
                    clean = words.replace('Father : ','')
                    Father = Father + clean
                if check_space(words) == 0 and check_case(words) == 1 and re.search('^[^.]*$',words):
                    Father = Father +  ' ' + words
        except TypeError:
            pass
        #Getting the Names  
        if len(Father) != 0:
            farname = Father

        # Cleaning DOB & Year of birth
        Year = ''
        for words in Years:
            for n in words:
                if n.isdigit():
                    Year = Year + n

        if len(Year) != 0:
            dob = Year
        else:
            dob = re.search(r'(\d+/\d+/\d+)',text).group()

        #Getting Correct DOB
        if len(fno) == 1:
            dob = fno + dob

        # Cleaning Adhaar number details
        if len(aadhar_number) >= 14:
            pass

        else:
            print("Aadhar number not read")

        if len(aadhar_number) > 15:
           aadhar_number = aadhar_number[5:]

        adh = aadhar_number


    except:
        pass
    data = {}
    data['Name'] = name
    data['Father Name'] = farname
    data['DOB / YOB'] = dob
    data['Adhaar Number'] = adh
    data['Sex'] = sex
    data['ID Type'] = "Adhaar"

    return data
