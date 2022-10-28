import tkinter as tk
from tkinter import filedialog
import json
import pytesseract
import cv2 as cv
import numpy as np
from PIL import Image
import sys
import re
import os
import ftfy
from datetime import datetime
from dateutil import relativedelta
import requests         
# module which we made to read the text of the document
import pan_read
import pass_read
import aadhaar_read
import annexure_read
import ticket_read
import visa_read
import template_match
import orient_ppa
import orient_at
import io


# API URL
api_url = "https://dataseedtech.com/new-bpc/public/api/receivedocstatus"

# Function to Find a particular Word in a Sentence.
def findword(textlist, wordlist):
  for text in textlist:
    for word in wordlist:
      if re.search(word, text.lower()):
        return text.lower()

# Specifying the path
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

#User Input For Annexure
doc0 = "Y"

#Taking Incident Number Manually
in_num = "A10105"

#Files 
F1 = "sample_1/image - annexure.jpg"
F2 = "sample_1/image - passport.jpg"
F3 = "sample_1/image - pan.jpg"
#F4 = "image - aadhaar.jpg"
F5 = "sample_1/image - ticket.jpg"
F6 = "sample_1/image - visa.jpg"

# Validation Status Dict
veri_dict = {}
veri_list = []

# Adding the incident Number
veri_dict['incident_number'] = in_num

if doc0 == 'Y':
    print("Processing...")
    filename = F1
    doc_name = None

    #Orientation
    angle = orient_at.detect_angle(cv.imread(filename))
    if angle == 90:
      pass
    elif angle == 180:
      pass
    elif angle == 270:
      pass
    else:
      #Reading For Verification text
      image = cv.imread(filename,0)
      text = pytesseract.image_to_string(image, lang = 'eng', config = '--psm 4 --oem 3 -c tesseract_char_whitelist=ABCDEFG0123456789')
      veri_text = []
      lines = text.split('\n')
      for lin in lines:
          s = lin.strip()
          s = lin.replace('\n','')
          s = s.rstrip()
          s = s.lstrip()
          veri_text.append(s)

      #Verification
      annexure = findword(veri_text,['forex','card holder name','thomas cook india ltd'])

      #For Annexure Verification
      if annexure != None:
          if "forex" in annexure or 'card holder name' in annexure or 'thomas cook india ltd' in annexure:
              doc_name = 'annexure'
      else:
          print("\n")
          print("The Uploaded Document is Not Annexure")
          exit(0)

      # Extraction From Annexure
      if doc_name == 'annexure':
          lis = []
          text = annexure_read.extract_annexure(filename)
          data = annexure_read.annexure_read_data(text)
          lis.append(data)

        #Writing for JSON
      try:
          to_unicode = unicode
      except NameError:
          to_unicode = str

      #Writing the jsdon
      try:
          with io.open('info.json', 'w', encoding='utf-8') as outfile:
              data_dumps = json.dumps(lis, indent = 0)
              outfile.write(to_unicode(data_dumps))

      #Reading the JSON 
          with open('info.json', 'r', encoding = 'utf-8') as data_load:
              data_loaded = json.load(data_load)
          
          #User Input For Passport
          #print("Annexure Extraction Done")
          #Annexure Status
          annexurerule = 4
          veri_dict['Annexure_status'] = 4
          #print("\n")
          doc1 = "Y"

          #Verification
          if doc1 == "N":
              exit(0)

          else:

            filename = F2
            doc_name = None

            #Orientation
            angle = orient_ppa.detect_angle(cv.imread(filename))
            if angle == 90:
              pass
            elif angle == 180:
              pass
            elif angle == 270:
              pass
            else:
              #Reading For Verification text
              image = cv.imread(filename,0)
              text = pytesseract.image_to_string(image, lang = 'eng', config = '--psm 4 --oem 3 -c tesseract_char_whitelist=ABCDEFG0123456789')
              veri_text = []
              lines = text.split('\n')
              for lin in lines:
                  s = lin.strip()
                  s = lin.replace('\n','')
                  s = s.rstrip()
                  s = s.lstrip()
                  veri_text.append(s)

              #Verification
              passport = findword(veri_text,['republic of india','republic'])

              #For Passport Verification
              if passport != None:
                  if "republic of india" in passport or "republic" in passport:
                      doc_name = 'passport'
                      #match = template_match.doTemplateMatch(doc_name,filename)
              else:
                doc_name = 'Not Found'

              # Extraction From Passport
              if doc_name == 'passport':
                text = pass_read.extract_passport(filename)
                data = pass_read.pass_read_data(text)
                lis.append(data)
              elif doc_name == 'Not Found':
                data = {"Date of Birth": None, "Date of Expiry": None, "Date of Issue": None, "Father Name": None, "ID Type": "Passport", "Mother Name": None,
                        "Name": None, "Nationality": "INDIAN", "Passport No": None, "Place of Birth": None, 
                        "Place of Issue": None, "Sex": "M", "Spouse Name": None, "Surname": None, "Unique Code": None}
                lis.append(data)

              #Writing for JSON
              try:
                  to_unicode = unicode
              except NameError:
                  to_unicode = str

              #Writing the jsdon
              with io.open('info.json', 'w', encoding='utf-8') as outfile:
                  data_dumps = json.dumps(lis, indent = 0)
                  outfile.write(to_unicode(data_dumps))

              #Reading the JSON 
              with open('info.json', 'r', encoding = 'utf-8') as data_load:
                  data_loaded = json.load(data_load)

              #User Input
              #print("Passport Extraction Done")
              #print("\n")
              verify = "Y"

              if verify == "N":
                exit(0)

              else:
                  # Passport Number Rule
                  #passrulelist = []
                  if data_loaded[0]['Passport Number'] == None:
                    passrule1 = 3
                    passrule1res = 'OCR Fails to Read Annexure'
                  elif data_loaded[0]['Passport Number'] == None:
                    passrule1 = 3
                    passrule1res = 'OCR Fails to Read Passport'
                  elif data_loaded[0]['Passport Number'] == data_loaded[1]['Passport No']:
                    passrule1 = 4 # Verified
                    passrule1res = 'Verified'
                  else:
                    passrule1 = 2
                    passrule1res = 'Verification Failed'
                    #passrulelist.append(passrule1res)

                  try:
                    # Passport Name Vs Anexxure Name
                    pfm = data_loaded[1]['Name']
                    pfm = list(pfm.split(" "))
                    pfl = pfm[0] + " " + data_loaded[1]['Surname']
                    pfml = pfm[0] + " " + pfm[1] + " " + data_loaded[1]['Surname']
                    if data_loaded[0]['Card Holder Name'] == None:
                      passrule2 = 3
                      passrule1res = 'OCR Fails to Read Annexure'
                    elif data_loaded[0]['Card Holder Name'] == pfl or data_loaded[0]['Card Holder Name'] == pfml:
                      passrule2 = 4 #Verified
                      passrule2res = 'Verified'
                    else:
                      passrule2 = 2
                      passrule2res = 'Verification Failed'
                      #passrulelist.append(passrule2res)
                  except AttributeError:
                    passrule2 = 3
                    passrule2res = 'OCR Fails to Read Passport'
                    #passrulelist.append(passrule2res)
                  # Date of Issue Rule
                  if data_loaded[0]['D.O.I'] == None:
                    passrule3 = 3
                    passrule3res = 'OCR Fails to Read Annexure'
                  elif data_loaded[1]['Date of Issue'] == None:
                    passrule3 = 3
                    passrule3res = 'OCR Fails to Read Passport'
                  elif data_loaded[0]['D.O.I'] == data_loaded[1]['Date of Issue']:
                      passrule3 = 4 #Verified
                      passrule3res = 'Verified'
                  else:
                      passrule3 = 2
                      passrule3res = 'Verification Failed'
                      #passrulelist.append(passrule3res)
                  # Mother Name Rule
                  try:
                    pmn = data_loaded[1]['Mother Name']
                    pmn = list(pmn.split(" "))
                    if data_loaded[0]['Mother Name'] == None:
                      passrule4 = 3
                      passrule4res = 'OCR Fails to Read Annexure'
                    if data_loaded[0]['Mother Name'] == pmn[0]:
                      passrule4 = 4 #Verified
                      passrule4res = 'Verified'
                    else:
                      passrule4 = 2
                      passrule4res = 'Verification Failed'
                      #passrulelist.append(passrule4res)
                  except AttributeError:
                    passrule4 = 3
                    passrule4res = 'OCR Fails to Read Passport'
                    #passrulelist.append(passrule4res)
                  # Date of Expiry Rule
                  if data_loaded[0]['D.O.E'] == None:
                    passrule5 = 3
                    passrule5res = 'OCR Fails to Read Annexure'
                  elif data_loaded[1]['Date of Expiry'] == None:
                    passrule5 = 3
                    passrule5res = 'OCR Fails to Read Passport'
                  if data_loaded[0]['D.O.E'] == data_loaded[1]['Date of Expiry']:
                      passrule5 = 4 #Verified
                      passrule5res = 'Verified'
                  else:
                      passrule5 = 2
                      passrule5res = 'Verification Failed'
                      #passrulelist.append(passrule5res)
                  
                  # Checking Validation of Passport
                  if passrule1 and passrule2 and passrule3 and passrule4 and passrule5 == 4:
                    veri_dict['passport_status'] = 3 #Still Not Keeping Verified as Signature Not Verified
                    #veri_dict['passport_reasons'] = 'All Passport Rule Matched'
                  elif passrule1 == 4:
                    veri_dict['passport_status'] = 3
                  else:
                    veri_dict['passport_status'] = 2
                    #Adding Passport Reasons
                    veri_dict['passport_reasons'] = passrule1res + ',' + ' ' + passrule2res + ',' + ' ' + passrule3res + ',' + ' ' + passrule4res + ',' + ' ' + passrule5res

              #print("Passport Verification Done")

              #User Input For PAN Card
              #print("\n")
              doc2 = "Y"

              #Verification
              if doc2 == "N":
                exit(0)

              else:

                filename = F3
                doc_name = None
                '''
                #Orientation
                angle = orient_ppa.detect_angle(cv.imread(filename))
                if angle == 90:
                  pass
                elif angle == 180:
                  pass
                elif angle == 270:
                  pass
                else:
                '''
                #Reading For Verification text
                image = cv.imread(filename,0)
                text = pytesseract.image_to_string(image, lang = 'eng', config = '--psm 4 --oem 3 -c tesseract_char_whitelist=ABCDEFG0123456789')
                veri_text = []
                lines = text.split('\n')
                for lin in lines:
                  s = lin.strip()
                  s = lin.replace('\n','')
                  s = s.rstrip()
                  s = s.lstrip()
                  veri_text.append(s)

                #Verification
                pan = findword(veri_text,['govt. of india','income','tax','department','permanent'])
                #For Pan Verification
                if pan != None:
                  if "govt. of india" in pan or "income" in pan or "tax" in pan or "department" in pan or "permanent" in pan:
                    doc_name = 'pan'
                    match = template_match.doTemplateMatch(doc_name,filename)
                else:
                    doc_name = "Not Found"
                    match = []

                # Extraction From PAN Card
                if doc_name == 'pan' and len(match) >= 2:
                  text = pan_read.extract_pan(filename)
                  data = pan_read.pan_read_data(text)
                  lis.append(data)
                elif doc_name == 'Not Found' and len(match) == 0:
                  data = { "Date of Birth": None, "Father Name": None, "ID Type": "PAN", "Name": None, "PAN": None}
                  lis.append(data)

                #Writing for JSON
                try:
                    to_unicode = unicode
                except NameError:
                    to_unicode = str

                #Writing the jsdon
                with io.open('info.json', 'w', encoding='utf-8') as outfile:
                  data_dumps = json.dumps(lis, indent = 0)
                  outfile.write(to_unicode(data_dumps))

                #Reading the JSON 
                with open('info.json', 'r', encoding = 'utf-8') as data_load:
                  data_loaded = json.load(data_load)

                #User Input
                #print("PAN Extraction Done")
                #print("\n")
                verify = "Y"

                if verify == "N":
                  exit(0)
                else:
                  # PAN Name Vs Annexure Name
                  try:
                    #panrulelist = []
                    pname = data_loaded[2]['Name']
                    pname = list(pname.split(" "))
                    pname = pname[0] + " " + pname[2]
                    if data_loaded[0]['Card Holder Name'] == None:
                      panrule1 = 3
                      panrule1res = 'OCR Fails to Read Annexure'
                    if data_loaded[0]['Card Holder Name'] == pname:
                        panrule1 = 4 #Verified   
                        panrule1res = 'Verified'
                    else:
                        panrule1 = 2
                        panrule1res = 'Verification Failed'
                        #panrulelist.append(panrule1res)
                  except AttributeError:
                    panrule1 = 3 
                    panrule1res = 'OCR Fails to Read PAN Card'
                    #panrulelist.append(panrule1res)
                  # PAN DOB Vs Annexure DOB
                  adob = data_loaded[0]['D.O.B']
                  adob = adob.replace('.','/').replace('-','/')
                  try:
                    if data_loaded[2]['Date of Birth'] == None:
                      panrule2 = 3 
                      panrule2res = 'OCR Fails to Read PAN Card'
                    if data_loaded[2]['Date of Birth'] == adob:
                        panrule2 = 4 #Verified
                        panrule2res = 'Verified'
                    else:
                        panrule2 = 2
                        panrule2res = 'Verification Failed'
                        #panrulelist.append(panrule2res)
                  except AttributeError:
                    panrule2 = 3
                    panrule2res = 'OCR Fails to Read PAN Card'
                    #panrulelist.append(panrule2res)

                  # Valiadtion of PAN
                  if panrule1 and panrule2 == 4:
                    veri_dict['pan_card_status'] = 4
                  else:
                    veri_dict['pan_card_status'] = 2
                    veri_dict['pan_card_reasons'] = panrule1res + ',' + ' ' + panrule2res

                  #print("PAN verification Done")
             
              #User Input For Ticket
              #print("\n")
              doc4 = "Y"

              #Verification
              if doc4 == "N":
                exit(0)
              else:

                filename = F5
                doc_name = None

                #Reading For Verification text
                image = cv.imread(filename,0)
                text = pytesseract.image_to_string(image, lang = 'eng', config = '--psm 4 --oem 3 -c tesseract_char_whitelist=ABCDEFG0123456789')
                veri_text = []
                lines = text.split('\n')
                for lin in lines:
                  s = lin.strip()
                  s = lin.replace('\n','')
                  s = s.rstrip()
                  s = s.lstrip()
                  veri_text.append(s)
                #Verification
                ticket = findword(veri_text,['flight','airlines','airines','terminal'])
                #For Ticket Verification
                if ticket != None:
                  if 'flight' in ticket or 'airlines' in ticket or 'airines' in ticket or 'terminal' in ticket:
                    doc_name = 'ticket'
                else:
                    print("\n")
                    print("The Uploaded Document is Not Ticket")
                    exit(0)

                #Checking Accuracy of the templates 
                if doc_name == 'ticket':
                  text = ticket_read.extract_ticket(filename)
                  data = ticket_read.ticket_read_data(text)
                  lis.append(data)

                #Writing for JSON
                try:
                    to_unicode = unicode
                except NameError:
                    to_unicode = str

                #Writing the jsdon
                with io.open('info.json', 'w', encoding='utf-8') as outfile:
                    data_dumps = json.dumps(lis, indent = 0)
                    outfile.write(to_unicode(data_dumps))

                #Reading the JSON 
                with open('info.json', 'r', encoding = 'utf-8') as data_load:
                    data_loaded = json.load(data_load)

                #User Input
                #print("Ticket Extraction Done")
                #print("\n")
                verify = "Y"

                if verify == "N":
                  exit(0)
                else:
                  #ticketrulelist = []
                  # Ticket Date of Travel Vs BPC Travel Port
                  try:
                    if data_loaded[3]['Date of Travel'] == None:
                      ticketrule1 = 3
                      ticketrule1res = 'OCR Fails to Read Ticket'
                    elif data_loaded[3]['Date of Travel'] == None:
                      ticketrule1 = 3
                      ticketrule1res = 'OCR Fails to Read Passport'
                    elif data_loaded[3]['Date of Travel'] == data_loaded[0]['Travel Date']:
                      ticketrule1 = 4 #Verified
                      ticketrule1res = 'Verified'
                    else:
                      ticketrule1 = 2
                      ticketrule1res = 'Verification Failed'
                      #ticketrulelist.append(ticketrule1res)
                  except IndexError:
                    if data_loaded[2]['Date of Travel'] == None:
                      ticketrule1 = 3
                      ticketrule1res = 'OCR Fails to Read Ticket'
                    elif data_loaded[2]['Date of Travel'] == None:
                      ticketrule1 = 3
                      ticketrule1res = 'OCR Fails to Read Passport'
                    elif data_loaded[2]['Date of Travel'] == data_loaded[0]['Travel Date']:
                      ticketrule1 = 4 #Verified
                      ticketrule1res = 'Verified'
                    else:
                      ticketrule1 = 2
                      ticketrule1res = 'Verification Failed'
                      #ticketrulelist.append(ticketrule1res)


                  # Ticket Date of Return Vs Within 6 months from date of travel
                  # get two dates
                  try:
                    d1 = data_loaded[3]['Date of Travel']
                    d2 = data_loaded[3]['Date of Return']
                  except IndexError:
                    d1 = data_loaded[2]['Date of Travel']
                    d2 = data_loaded[2]['Date of Return']
                  # convert string to date object
                  try:
                    start_date = datetime.strptime(d1, "%d/%m/%Y")
                    end_date = datetime.strptime(d2, "%d/%m/%Y")
                    # Get the relativedelta between two dates
                    delta = relativedelta.relativedelta(end_date, start_date)
                    if delta.months < 6:
                      ticketrule2 = 4 #Verified
                      ticketrule2res = 'Verified'
                    elif delta.months == 6 and delta.days == 0:
                      ticketrule2 = 4 #Verified
                      ticketrule2res = 'Verified'
                    else:
                      ticketrule2 = 2
                      ticketrule2res = 'Verification Failed'
                      #ticketrulelist.append(ticketrule2res)
                  except TypeError:
                    ticketrule2 = 3
                    ticketrule2res = 'OCR Fails to Read Ticket'
                    #ticketrulelist.append(ticketrule2res)

                # Validation of Ticket
                  if ticketrule1 and ticketrule2 == 4:
                    veri_dict['ticket_status'] = 4
                  else:
                    veri_dict['ticket_status'] = 2
                    veri_dict['ticket_reasons'] = ticketrule1res + ',' + ' ' + ticketrule2res 

                  #print("Ticket Verification Done")

              #User Input For Visa
              #print("\n")
              doc5 = "Y"

              #Verification
              if doc5 == "N":
                exit(0)
              else:

                filename = F6
                doc_name = None

                #Reading For Verification text
                image = cv.imread(filename,0)
                text = pytesseract.image_to_string(image, lang = 'eng', config = '--psm 4 --oem 3 -c tesseract_char_whitelist=ABCDEFG0123456789')
                veri_text = []
                lines = text.split('\n')
                for lin in lines:
                  s = lin.strip()
                  s = lin.replace('\n','')
                  s = s.rstrip()
                  s = s.lstrip()
                  veri_text.append(s)

                #For Visa Verifcation
                visa = findword(veri_text,['visa','evisa'])
                if visa != None:
                  doc_name = 'visa'
                else:
                  print("\n")
                  print("The Uploaded Document is Not Visa")
                  exit(0)

                #Checking Accuracy of the templates 
                if doc_name ==  'visa':
                  text = visa_read.extract_visa(filename)
                  data = visa_read.visa_read_data(text)
                  lis.append(data)

                #Writing for JSON
                try:
                    to_unicode = unicode
                except NameError:
                    to_unicode = str

                #Writing the jsdon
                with io.open('info.json', 'w', encoding='utf-8') as outfile:
                    data_dumps = json.dumps(lis, indent = 0)
                    outfile.write(to_unicode(data_dumps))

                #Reading the JSON 
                with open('info.json', 'r', encoding = 'utf-8') as data_load:
                    data_loaded = json.load(data_load)

                #User Input
                #print("Visa Extraction Done")
                #print("\n")
                verify = "Y"

                if verify == "N":
                  exit(0)
                else:
                  #visarulelist = []
                  # Calculating the difference between Expiry & Issue Date
                  try:
                    if data_loaded[4]['Date of Issue'] and data_loaded[4]['Date of Expiry'] != None:
                      d3 = data_loaded[4]['Date of Issue']
                      d4 = data_loaded[4]['Date of Expiry']
                    else:
                      d3 = d1
                      d4 = d2
                  except IndexError:
                    if data_loaded[3]['Date of Issue'] and data_loaded[3]['Date of Expiry'] != None:
                      d3 = data_loaded[3]['Date of Issue']
                      d4 = data_loaded[3]['Date of Expiry']
                    else:
                      d3 = d1
                      d4 = d2
                  # convert string to date object
                  start_date1 = datetime.strptime(d3, "%d/%m/%Y")
                  end_date1 = datetime.strptime(d4, "%d/%m/%Y")

                  # Get the relativedelta between two dates
                  try:
                    delta1 = relativedelta.relativedelta(end_date1, start_date1)
                    if delta.months > delta1.months:
                      visarule1 = 4 #Verified
                      visarule1res = 'Verified'
                    elif delta.months >= delta1.months and delta.days == delta1.days:
                      visarule1 = 4 #Verified
                      visarule1res = 'Verified'
                    else:
                      visarule1 = 2
                      visarule1res = 'Verification Failed'
                      #visarulelist.append(visarule1res)
                  except NameError:
                    visarule1 = 3
                    visarule1res = 'OCR Fails to Read Visa'
                    #visarulelist.append(visarule1res)

                  # Validation of Visa
                  if visarule1 == 4:
                    veri_dict['visa_status'] = 4
                  else:
                    veri_dict['visa_status'] = 2
                    veri_dict['visa_reasons'] = visarule1res
                  
                  #print("Visa Verification Done")       

              # Making a Json
                veri_list.append(veri_dict)
                #Writing the json
                with io.open('status.json', 'w', encoding='utf-8') as statusfile:
                    status_dumps = json.dumps(veri_list, indent = 0)
                    statusfile.write(to_unicode(status_dumps))

                #Reading the JSON 
                with open('status.json', 'r', encoding = 'utf-8') as status_load:
                    status_loaded = json.load(status_load)

                # To See Status
                #print("\n")
                see_status = "N"

                if see_status == 'Y':
                  print("\n-----Validation Status Details ----")
                  print("\nIncident Number: ",status_loaded[0]['incident_number'])
                  print("\nPassport Status: ",status_loaded[0]['passport_status'])
                  try: 
                    print("\nPassport Reasons: ",status_loaded[0]['passport_reasons'])
                  except KeyError:
                    pass
                  try:
                    print("\nPan Card Status: ",status_loaded[0]['pan_card_status'])
                    print("\nPan Card Reasons: ",status_loaded[0]['pan_card_reasons'])
                  except KeyError:
                    pass
                  print("\nTicket Status: ",status_loaded[0]['ticket_status'])
                  try:
                    print("\nTicket Reasons: ",status_loaded[0]['ticket_reasons'])
                  except KeyError:
                    pass
                  print("\nVisa Status: ",status_loaded[0]['visa_status'])
                  try:
                    print("\nVisa Reasons: ",status_loaded[0]['visa_reasons'])
                  except KeyError:
                    pass
                  print("\n-----------------------------------")
                else:
                  print("\nJson File of Validation Status is Created")
                  exit(0)

                data = [{
                        "incident_number": "A002411",
                        "annexure_status":4,
                        "passport_status":3,
                        "passport_reasons": "ocr worked, check for osv",
                        "pan_card_status": 3,
                        "pan_card_reasons": "OCR failed",
                        "ticket_status": 3,
                        "ticket_reasons": "Ticket Date of Travel Matched,Ticket Date of Return Not Matched",
                        "visa_status": 3,
                        "visa_reasons": "Data of return within validity, Entry port not matched, Exit port not matched"
                        }]


                '''
                #data = {"incidant_no": "A000001", "passport_status": 0, "annexure_status": 1, "pan_card_status": 1}
                # Sending Data to the API 
                try:
                  # sending post request and saving response as response object
                  r = requests.post(url = api_url, data = status_loaded)
                except Api_Exception_error: 
                  print("Post API not processed correctly")

                # extracting response text 
                pastebin_url = r.text
                print("\n")
                print("The pastebin URL is:%s"%pastebin_url)
                '''
      except NameError:
        print("\n------------------------- False Documents ---------------------------")
        print("\n The Uploaded Document is Not Correct Please Upload Correct Documents")
        k = input("\n\nPress Enter To EXIT")
        exit(0)

else:
    exit(0)


