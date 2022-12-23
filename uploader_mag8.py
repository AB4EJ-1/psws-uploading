# Uplooader for sending files from Magnetometer to Central Control System
# Author: W. Engelke, AB4EJ , University of Alabama
# This script uploads magnetometer data to Central Control System. 
# mag_settings MUST be correct, or the data will not be uploaded and/or the database will not be updated
# Note that a data upload acts as a heartbeat and will mark the station as active.

# Optional Argument: -h   - indicates that all history files in logs database should be uploaded.
#   If this argument is omitted, then just the current day is uploaded 

import os, sys
from datetime import datetime
import pytz
from pytz import timezone
import time
import configparser

userArg = ""

if len(sys.argv) > 1:  # did user provide an argument
    userArg = str(sys.argv[1]) # look for -h
    if userArg != "-h":
        print("argument supplied: ",userArg," was not recognized; only -h supported")


parser = configparser.ConfigParser(allow_no_value=True)
parser.read('uploader.config')

# mag_settings for lftp
throttle  = parser['mag_settings']['throttle']

# Local data storage area

orig_path = parser['mag_settings']['orig_path']
temp_path = parser['mag_settings']['temp_path']

targetDir = parser['mag_settings']['targetDir']
prefix    = parser['profile']['prefix']

# The following mag_settings control the upload; see documentation

obs            = parser['mag_settings']['obs']

theStationID   = parser['profile']['theStationID']
theToken       = parser['profile']['token_value']  # Do not share this or post publicly
central_host   = parser['profile']['central_host']
instrumentName = parser['mag_settings']['instrumentName']
sleepTime      = int(parser['mag_settings']['sleepTime'])

print("Uploader starting, using settings as follows:")
print("Throttle: " + throttle + " bytes/sec. limit")
print("orig_path: "  + orig_path)
print("temp_path: " + temp_path)
print("target directory: " + targetDir)
print("prefix: " + prefix)
print("observation name: " + obs)
print("Station ID: " + theStationID)
print("central host URL: " + central_host)
print("instrument name: " + instrumentName)
print("Sleep time between uploads: " + str(sleepTime) + "sec.")
print("\n")

while True:

    command = "rm " + temp_path + "/*.zip"  # clean out any existing files in temp area
    print("do command:", command)
    os.system(command)
    
    if userArg == "-h": # are we doing full historical upload?
    # get directory list of files in logs directory
        fileList = os.listdir(orig_path)
        for thisfile in fileList:
            print("filename:",thisfile)
            filepart = thisfile.split("-")
            if filepart[2] != "runmag.log":
                continue
            filedate = filepart[1][0:4] + "-" + filepart[1][4:6] + "-" + filepart[1][6:9]
            obsname = "OBS" + filedate + "T00:00"

            print("obsname=",obsname)
            inpath = os.path.join(orig_path, thisfile)
            outpath = os.path.join(temp_path, obsname + ".zip")
            command = "zip -j " + outpath + " " + inpath
            print("\n" ,command, "\n")
            os.system(command)
    else: # just handle the current day's file
        now = datetime.now(pytz.utc)
        currentFile = prefix + "-" + now.strftime('%Y%m%d') + "-runmag.log"
        filedate = now.strftime('%Y-%m-%d')
        print("current file:",currentFile)
        obsname = "OBS" + filedate + "T00:00"
        print("Observation=",obsname)
        inpath = os.path.join(orig_path, currentFile)
        outpath = os.path.join(temp_path, obsname + ".zip")
        command = "zip -j " + outpath + " " + inpath
        print("\n" ,command, "\n")
        os.system(command)
    
    now = datetime.now(pytz.utc)
    DR_pending = now.strftime('%Y-%m-%dT%H:%M')
    print ("Upload starting " + DR_pending)
  # the below adds set net timeout, max retries & reconnect interval base  
    command = "lftp -e 'set net:limit-rate " + throttle + ";set net:timeout 5;set net:max-retries 2;set net:reconnect-interval-base 5;mirror --exclude README* -R --verbose " + temp_path + " " + targetDir + ";chmod o+rx " + targetDir + ";mkdir m" + obs + "_#" + instrumentName + "_#" + DR_pending + ";exit' -u " + theStationID + "," + theToken + " sftp://" + central_host + " " 
    print("\nUpload command = '" + command + "'\n")

    print("Starting upload...")
    os.system(command)
    time.sleep(sleepTime)   # run every 15 mins
