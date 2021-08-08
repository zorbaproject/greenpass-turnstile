#!/usr/bin/python3

#sudo apt-get install pcscd
# sudo apt-get install libccid
# sudo apt-get install opensc
#sudo apt-get install swig
#sudo apt-get install python3-pyscard

from smartcard.System import readers

#sudo apt-get install python3-opencv python3-sip libjasper-dev libatlas-base-dev -y
#pip3 install opencv-contrib-python==4.1.0.25

import cv2
from PIL import Image

import beepy as beep

import subprocess
import array
import json
import os
import sys
import time
from datetime import datetime


relay = 17


cfgfile = os.path.abspath(os.path.dirname(sys.argv[0]))+"/green-pass.json"
logfile = os.path.abspath(os.path.dirname(sys.argv[0]))+"/green-pass.log"

try:
  import RPi.GPIO as GPIO
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(relay, GPIO.OUT)
  rpi = True
except:
  rpi = False

config = {}

reader = None
try:
  r = readers()
  if len(r) == 0:
      print("No card reader found")
      sys.exit()
  reader = r[0]
  #print("Sto usando: "+str(reader))
except:
  print("Undefined error loading Smart Card Reader")
  pass

def getConfig():
  global cfgfile
  global config
  text_file = open(cfgfile, "r")
  mytext = text_file.read()
  text_file.close()
  config = json.loads(mytext)

def open_door():
    global relay
    if rpi:
        GPIO.output(relay, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(relay, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(relay, GPIO.LOW)

def checkGP_text(gpText):
  #Thanks to: https://github.com/panzi/verify-ehc
  #process = subprocess.Popen([os.path.abspath(os.path.dirname(sys.argv[0]))+'/verify-ehc/verify_ehc.py', "'gpText'"], stdout=subprocess.PIPE)
  #stdout = process.communicate()[0]
  #myoutput = stdout.decode('ascii')
  tmpfile = '/tmp/greenpass.json'
  os.system(os.path.abspath(os.path.dirname(sys.argv[0]))+"/verify-ehc/verify_ehc.py '"+gpText+"' > "+tmpfile)
  text_file = open(tmpfile, "r")
  myoutput = text_file.read()
  text_file.close()
  GPdata = {}
  GPpayload = ""
  payl = False
  for line in myoutput.split("\n"):
      if "Is Expired" in line:
        if "False" in line:
          GPdata["expired"] = False
        else:
          GPdata["expired"] = True
      if "Signature Valid" in line:
        if "True" in line:
          GPdata["signature_valid"] = True
        else:
          GPdata["signature_valid"] = False
      if payl:
        GPpayload = GPpayload + line
      if "Payload" in line:
        payl = True
  GPdata["payload"] = json.loads(GPpayload.replace("\n", "").replace("\r", ""))
  return GPdata

def getTSdata():
  #Thanks to: https://www.mmxforge.net/index.php/sviluppo/python/item/9-lettura-dei-dati-della-tessera-sanitaria-con-python
  global reader
  try:
    connection = reader.createConnection()
    connection.connect()
  except:
    return {}
  #Seleziona del MF
  #CLS 00, istruzione A4 (seleziona file), P1 = P2 = 0 (seleziona per ID),
  #Lc: 2, Data: 3F00 (id del MF)
  SELECT_MF = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x00]
  data, sw1, sw2 = connection.transmit(SELECT_MF)
  #se tutto è andato a buon fine sw1 e sw2 contengono
  #rispettivamente i valori 0x90 e 0x00 il corrispettivo del 200 in HTTP

  #Seleziona del DF1...vedi sopra
  SELECT_DF1 = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x11, 0x00]
  data, sw1, sw2 = connection.transmit(SELECT_DF1)

  #Seleziona del file EF.Dati_personali... vedi sopra sopra
  SELECT_EF_PERS = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x11, 0x02]
  data, sw1, sw2 = connection.transmit(SELECT_EF_PERS)

  #leggiamo i dati
  #CLS 00, istruzione B0 (leggi i dati binari contenuti nel file
  READ_BIN = [0x00, 0xB0, 0x00, 0x00, 0x00, 0x00]
  data, sw1, sw2 = connection.transmit(READ_BIN)

  #Note:
  #https://www.agid.gov.it/sites/default/files/repository_files/documentazione/filesystemcns_20160610.pdf
  #https://www.agid.gov.it/sites/default/files/repository_files/documentazione_trasparenza/lineeguidacnsv3.0.pdf

  #data contiene i dati anagrafici in formato binario
  #trasformiamo il tutto in una stringa
  stringa_dati_personali = array.array('B', data).tobytes()
  dimensione = int(stringa_dati_personali[0:6],16)

  dati_TS = {}

  prox_field_size = int(stringa_dati_personali[6:8], base=16)
  da = 8
  a = da + prox_field_size
  if prox_field_size > 0:
    codice_emettitore = stringa_dati_personali[da:a]
    dati_TS["emettitore"] = str(codice_emettitore.decode("ascii"))

  da = a
  a +=2
  prox_field_size = int(stringa_dati_personali[da:a], base=16)
  da=a
  a += prox_field_size
  if prox_field_size > 0:
    data_rilascio_tessera = stringa_dati_personali[da:a]
    dati_TS["rilascio"] = str(data_rilascio_tessera[0:2].decode("ascii"))+"/"+str(data_rilascio_tessera[2:4].decode("ascii"))+"/"+str(data_rilascio_tessera[-4:].decode("ascii"))

  da = a
  a +=2
  prox_field_size = int(stringa_dati_personali[da:a], 16)
  da=a
  a += prox_field_size
  if prox_field_size > 0:
    data_scadenza_tessera = stringa_dati_personali[da:a]
    dati_TS["scadenza"] = str(data_scadenza_tessera[0:2].decode("ascii"))+"/"+str(data_scadenza_tessera[2:4].decode("ascii"))+"/"+str(data_scadenza_tessera[-4:].decode("ascii"))

  da = a
  a +=2
  prox_field_size = int(stringa_dati_personali[da:a], 16)
  da=a
  a += prox_field_size
  if prox_field_size > 0:
    cognome = stringa_dati_personali[da:a]
    dati_TS["cognome"] = str(cognome.decode("ascii"))

  da = a
  a +=2
  prox_field_size = int(stringa_dati_personali[da:a], 16)
  da=a
  a += prox_field_size
  if prox_field_size > 0:
    nome = stringa_dati_personali[da:a]
    dati_TS["nome"] = str(nome.decode("ascii"))

  da = a
  a +=2
  prox_field_size = int(stringa_dati_personali[da:a], 16)
  da=a
  a += prox_field_size
  if prox_field_size > 0:
    data_nascita = stringa_dati_personali[da:a]
    dati_TS["nato"] = str(data_nascita[0:2].decode("ascii"))+"/"+str(data_nascita[2:4].decode("ascii"))+"/"+str(data_nascita[-4:].decode("ascii"))

  da = a
  a +=2
  prox_field_size = int(stringa_dati_personali[da:a], 16)
  da=a
  a += prox_field_size
  if prox_field_size > 0:
    sesso = stringa_dati_personali[da:a]
    dati_TS["sesso"] = str(sesso.decode("ascii"))

  da = a
  a +=2
  prox_field_size = int(stringa_dati_personali[da:a], 16)
  da=a
  a += prox_field_size
  if prox_field_size > 0:
    statura = stringa_dati_personali[da:a]
    dati_TS["statura"] = str(statura.decode("ascii"))

  da = a
  a +=2
  prox_field_size = int(stringa_dati_personali[da:a], 16)
  da=a
  a += prox_field_size
  if prox_field_size > 0:
    CF = stringa_dati_personali[da:a]
    dati_TS["CF"] = str(CF.decode("ascii"))

  da = a
  a +=2
  prox_field_size = int(stringa_dati_personali[da:a], 16)
  da=a
  a += prox_field_size
  if prox_field_size > 0:
    cittadinanza = stringa_dati_personali[da:a]
    dati_TS["cittadinanza"] = str(cittadinanza.decode("ascii"))

  da = a
  a +=2
  prox_field_size = int(stringa_dati_personali[da:a], 16)
  da=a
  a += prox_field_size
  if prox_field_size > 0:
    comune_nascita = stringa_dati_personali[da:a]
    dati_TS["comune_nascita"] = str(comune_nascita.decode("ascii"))

  da = a
  a +=2
  prox_field_size = int(stringa_dati_personali[da:a], 16)
  da=a
  a += prox_field_size
  if prox_field_size > 0:
    stato_nascita = stringa_dati_personali[da:a]
    dati_TS["stato_nascita"] = str(stato_nascita.decode("ascii"))

  return dati_TS


def isCertValid(GPdata,TSdata):
    global config
    valid = True
    err = ""
    if GPdata["expired"]:
      valid = False
      err = "Il certificato è scaduto"
    if not GPdata["signature_valid"]:
      valid = False
      err = "Il certificato non è firmato da una autorità sanitaria"
    if len(TSdata) > 1:
      try:
        TSdob = TSdata["nato"].split("/")[2] + "-" + TSdata["nato"].split("/")[1] + "-" + TSdata["nato"].split("/")[0]
      except:
        TSdob = ""
      if GPdata["payload"]["nam"]["fn"].lower() != TSdata["cognome"].lower() or GPdata["payload"]["nam"]["gn"].lower() != TSdata["nome"].lower() or GPdata["payload"]["dob"].lower() != TSdob.lower():
        valid = False
        err = "Il certificato non appartiene alla persona identificata dalla tessera sanitaria"
    else:
      valid = False
      err = "Certificato valido per "+str(GPdata["payload"]["nam"]["gn"])+ " "+GPdata["payload"]["nam"]["fn"]+" ma nessuna tessera sanitaria rilevata."
      if config["interactive"]:
        print(err+" Confermi che il certificato appartiene a questa persona?")
        ch = input()
        if "y" in ch.lower() or "s" in ch.lower():
          valid = True
    return valid, err


def getQRfromCamera():
  # set up camera object
  cap = cv2.VideoCapture(0)

  # QR code detection object
  detector = cv2.QRCodeDetector()
  print("Waiting for QR code")

  while True:
    # get the image
    _, img = cap.read()

    #qrtools is not available for python3 on buster
    cv2.imwrite('/tmp/qrimage.png',img)
    process = subprocess.Popen([os.path.abspath(os.path.dirname(sys.argv[0]))+'/qrcodereader-py2.py', '/tmp/qrimage.png'], stdout=subprocess.PIPE)                                                                                                   
    stdout = process.communicate()[0]
    data = stdout.decode('ascii')
    ## apt install python3-qrtools
    #from qrtools.qrtools import QR
    #myQR = QR(filename = '/tmp/qrimage.png')
    #myQR.decode()
    #data = str(myQR.data)

    if len(data) > 0 and "NULL" not in data:
        break

    # display the image preview only if we have Xorg available
    xorg = False
    if 'DISPLAY' in os.environ:
        if os.environ['DISPLAY'] != None and os.environ['DISPLAY'] != "":
          xorg = True
    if xorg:
      cv2.imshow("code detector", img)
      if(cv2.waitKey(1) == ord("q")):
          break
    time.sleep(0.1)
  # free camera object and exit
  cap.release()
  cv2.destroyAllWindows()
  
  return data



getConfig()

active = True

while active:
    beep.beep(4)
    gpText = getQRfromCamera()

    print("QRcode:"+gpText)

    GPdata = checkGP_text(gpText)
    #print(GPdata)

    TSdata = getTSdata()
    #print(TSdata)

    val,err = isCertValid(GPdata,TSdata)

    msg = ""
    status = "ERROR"
    if val:
        msg = "OK: certificato valido e documento corrispondente per "+str(GPdata["payload"]["nam"]["gn"])+" "+str(GPdata["payload"]["nam"]["fn"])+", puoi entrare."
        status = "OK"
        beep.beep(5)
        open_door()
    else:
        msg = "ERRORE: "+err
        beep.beep(3)
    print(msg)
    
    if config["log"]:
        try:
            cf = TSdata["CF"]
        except:
            cf = ""
        
        logline = str(datetime.now()) + "," + status + "," + str(cf) +"," + msg
        with open(logfile, "a", encoding='utf-8') as myfile:
            myfile.write(logline+"\n")
    time.sleep(1)
