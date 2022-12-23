# Uplooader for sending DRF files from Grape1 to Central Control System
# Author: W. Engelke, AB4EJ , University of Alabama, 2022
# This script depends on a configuration file:  uploader.confg
# Settings MUST be correct, or the data will not be uploaded and/or the database will not be updated
# Note that a data upload acts as a heartbeat and will mark the station as active.

import os
from datetime import datetime, timezone
import time
import configparser

parser = configparser.ConfigParser(allow_no_value=True)
parser.read('uploader.config')

# settings for lftp
throttle  = parser['spectrum_settings']['throttle']

#source_path  = '/media/ab4ej/RFdata/narrow19/'
source_path  = parser['spectrum_settings']['source_path']

now = datetime.now(timezone.utc)
DR_pending = now.strftime('%Y-%m-%dT%H:%M')
print ("Upload starting " + DR_pending)

#obs = "OBS2022-11-22T20:00"   # observation name
obs = parser['spectrum_settings']['obs']


#theNode      = 'N000004'
#theToken     = 'TooMuchnoiseUPSTAIRS2@'
#central_host = 'pswsnetwork.caps.ua.edu'
#instrumentName = "Grape19"

theStationID   = parser['profile']['theStationID']
theToken       = parser['profile']['token_value']  # Do not share this or post publicly
central_host   = parser['profile']['central_host']
instrumentName = parser['spectrum_settings']['instrumentName']
sleepTime      = int(parser['spectrum_settings']['sleepTime'])


  
while True:
    
    now = datetime.now(timezone.utc)
    DR_pending = now.strftime('%Y-%m-%dT%H:%M')
    print(" ")
    print("Upload starting, time: ",DR_pending)
    
    triggerDir = "c" + obs + "_#" + instrumentName + "_#" + DR_pending
    
    # the below is for continuous upload; in filename we use instrumentID instead of DR_pending
    command = "lftp -e 'set net:limit-rate " + throttle + ";mirror --exclude tmp.* -R --verbose " + source_path + " " + obs + ";chmod 775 " + obs + ";mkdir " + triggerDir + ";chmod 775 " + triggerDir + ";exit' -u " + theStationID + "," + theToken + " sftp://" + central_host + " " 


    print("Upload command = '" + command + "'")
  #          log("Uploading, Node = " + theNode + " token = " + theToken, log_INFO)
    print("Starting upload...")
    os.system(command)
    time.sleep(1800) # wait 
