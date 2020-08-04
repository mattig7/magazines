#! python3
"""
downloadMagazines.py - Searches for and downloads magazines from specified sites.
Sites and magazine names are specified in a default json file, but the script will
 create one if it doesn't exist (so that you can change it and run the script again).
TODO: Fix the header. Add comments. Add json file for magazines. Add a function for downloading the site, then a function for downloading an actual pdf. Insert logging commands.
"""

import requests, bs4 
import os, logging, json, re
from pathlib import Path

desiredLogLevel = logging.DEBUG
logger = logging.getLogger('Logger for magazine download program')
logger.setLevel(desiredLogLevel) #Pass all message levels to the handlers by default

logFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)
streamHandler.setFormatter(logFormatter)

logger.addHandler(streamHandler)
logger.debug("Commenced initialiastion of logger and necessary parameters")

magDefsFile = Path("./mag_config.json")
logFile = Path("./mag.log")

logger.debug("Creating file handler for logging")

fileHandler = logging.FileHandler(logFile,mode='w') #overwrites previous log
fileHandler.setLevel(desiredLogLevel)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

logger.debug(f"Completed creating the filehandler for logging using file {logFile}")
logger.debug("Completed establishing logging capability")



def findAndDownloadLinks (URL, magName):
    """
    Function to search through a website and download all potential magazine links it finds.
    Will call itself recursively on subsites that look promising to try to find all the magazines present.
    """
    logger.debug("Commenced 'findAndDownloadLinks' function for {magName} with URL: {URL}.")
    
    logger.debug("Completed 'findAndDownloadLinks' function for {magName} with URL: {URL}.")

if __name__ == "__main__":
    """
    main function. Creates the magazine config file if not present, loads it and commences
    the program otherwise.
    """
    logger.debug("Commencing main function")
    magUrls = ""
    #If magazine definitions file exists, load it. Otherwise make one
    if not magDefsFile.exists():
        logger.debug(f"Magazine definitions file, {magDefsFile}, does not exist. Creating it")
        magUrls = {'hackspace': 'https://hackspace.raspberrypi.org/issues/','magpi': 'https://magpi.raspberrypi.org/issues/'}
        with open(magDefsFile, 'w') as outfile:
            json.dump(magUrls, outfile, indent=4)
        logger.debug(f"Finished creating magazine definitions file {magDefsFile} with data:\n{magUrls}")
    else:
        logger.debug(f"Found magazine definition file at {magDefsFile}. Loading data")
        with open(magDefsFile) as infile:
            magUrls = json.load(infile)
    logger.debug(f"Established magazine definitions as:\n{str(magUrls)}")

    # Call the functions to start the capability.



    logger.debug(f"Completed main function")
