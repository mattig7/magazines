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

from urllib.parse import urlparse, urljoin

# Config and logging default files
magDefsFile = Path("./mag_config.json")
logFile = Path("./mag.log")

# Set up logging
desiredLogLevel = logging.DEBUG
logger = logging.getLogger('Logger for magazine download program')
logger.setLevel(desiredLogLevel) #Pass all message levels to the handlers by default

logFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)
streamHandler.setFormatter(logFormatter)

logger.addHandler(streamHandler)
logger.debug("Commenced initialiastion of logger and necessary parameters")

logger.debug("Creating file handler for logging")

fileHandler = logging.FileHandler(logFile,mode='w') #overwrites previous log
fileHandler.setLevel(desiredLogLevel)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

logger.debug(f"Completed creating the filehandler for logging using file {logFile}")

logger.debug(f"Completed establishing logging capability")

def is_absolute(URL):
    """
    Function to check whether a URL is absolute or not.
    """
    return bool(URL.netloc)


def downloadLink(URL, magname):
    """
    Function to download a magazine that has been found.
    """
    logger.debug(f"Commencing function 'downloadLink' with:\nURL: {URL}\nmagname: {magname}")
    if not ".pdf" in URL:
        logger.debug(f"downloadLink called for a URL that does not contain a pdf file: {URL}. Returning without doing anything.")
        return
    
    Path("./magname").mkdir(exist_ok=True)
    
    # Download the file if doesn't exist
    #TODO UP TP HERE! COME BACK TO THIS.

    logger.debug(f"Completed function 'downloadLink' with:\nURL: {URL}\nmagname: {magname}")

def findAndDownloadLinks (URL, magName):
    """
    Function to search through a website and download all potential magazine links it finds.
    Will call itself recursively on subsites that look promising to try to find all the magazines present.
    """
    regex_GoodLink = re.compile(r"[Dd]ownload|(pdf|PDF)|[Nnext]")
    logger.debug(f"Commenced 'findAndDownloadLinks' function for {magName} with URL: {URL}.")
    # send any pdf file links straight to downloadLink function
    if ".pdf" in URL:
        logger.debug(f"findAndDownloadLinks function was given a pdf link: {URL}. Sending to downloadLink function and returning.")
        downloadLink(URL, magName)
        return

    #Download the URL
    logger.debug(f"Downloading site {URL}")
    try:
        res = requests.get(URL)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"There was a problem with {magname} from URL: {URL}:\n {e}")
    
    # Use Beautiful soup to find the links of interest
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    href = "href"
    #logger.debug(f"The site obtained from {URL} is:\n{soup.prettify()}")
    #logger.debug(f"The site ({URL}) main section is: \n{soup.body.main.prettify()}")
    for link in soup.body.main.select('a[href]'):
        logger.debug(f"Processing link with:\nText: {link.get_text()}\nhref:{link['href']}")
        urlParsed = urlparse(link["href"])
        # Want to follow all links on the page that mention download or pdf
        if not is_absolute(urlParsed):
            logger.debug(f"Attempting to join:\n{URL}\n{urlParsed.geturl()}") 
            urlParsed = urlparse(urljoin(URL, urlParsed.geturl()))
            logger.debug(f"Updated the relative href to be: {urlParsed.geturl()}")

        if ".pdf" in urlParsed.geturl():
            logger.debug(f"The phrase '.pdf' is in the link. Calling downloadLink method to get it!")
            downloadLink(urlParsed.geturl(), magname)
        elif regex_GoodLink.match(link.get_text()) and urlParsed.geturl() != URL:
            logger.debug(f"No '.pdf' in href, but found good link words in the text. Download site and check it!")
            findAndDownloadLinks(urlParsed.geturl(), magname)
        else:
            logger.debug(f"No PDF here and no good words. No action for this link")
            logger.debug(f"For reference, output of the regex match is {regex_GoodLink.match(link.get_text())}\nAnd the output of testing if urls are different is: {urlParsed.geturl() != URL}\nTherefore the if test should be: {bool(regex_GoodLink.match(link.get_text()) and urlParsed.geturl() != URL)}")
    logger.debug(f"Completed 'findAndDownloadLinks' function for {magName} with URL: {URL}.")

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
    for magname, URL in magUrls.items():
        logger.debug(f"Commencing downloading of {magname} for URL {URL}")
        findAndDownloadLinks(URL, magname)
    
    logger.debug(f"Completed main function")
