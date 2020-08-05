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
desiredLogLevel = logging.INFO
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
    logger.info(f"Commencing function 'downloadLink' with:\nURL: {URL}\nmagname: {magname}")
    if not ".pdf" in URL:
        logger.debug(f"downloadLink called for a URL that does not contain a pdf file: {URL}. Returning without doing anything.")
        return
    
    Path(f"./{magname}").mkdir(exist_ok=True)
    
    #Pull the filename out of the URL
    urlParsed = urlparse(URL)
    pdfFileName = urlParsed[2] #Path attribute of the url
    pdfFileName = pdfFileName[pdfFileName.rfind('/')+1:]
    pdfFileName = Path(magname)/Path(pdfFileName)
    logger.debug(f"Found the filename of the pdf to be {pdfFileName}")
    
    if pdfFileName.exists():
        logger.debug(f"The pdf file {pdfFileName} already exists. Not downloading")

    else:
        logger.debug(f"The pdf file {pdfFileName} doesn't exist. Downloading")
        try:
            res = requests.get(URL)
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"There was a problem with downloading: {pdfFileName}:\n {e}")
            return
        logger.debug(f"Opening file for writing: {pdfFileName}")
        f = open(pdfFileName, 'wb')
        logger.debug(f"Iterating through the request to download file")
        for chunk in res.iter_content(100000):
            f.write(chunk)

    logger.debug(f"Completed function 'downloadLink' with:\nURL: {URL}\nmagname: {magname}")

def findAndDownloadLinks (URL, magName):
    """
    Function to search through a website and download all potential magazine links it finds.
    Will call itself recursively on subsites that look promising to try to find all the magazines present.
    """
    regex_GoodLink = re.compile(r"(download|pdf|next)", flags=re.I)
    logger.info(f"Commenced 'findAndDownloadLinks' function for {magName} with URL: {URL}.")
    logger.debug(f"The regex to match for a good link text is {regex_GoodLink}")
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
        # Test for and follow promising links
        if ".pdf" in urlParsed.geturl():
            logger.debug(f"The phrase '.pdf' is in the link. Calling downloadLink method to get it!")
            downloadLink(urlParsed.geturl(), magname)
            logger.debug(f"Back in FindAndDownloadLinks function after downloading {URL}")
        elif regex_GoodLink.search(link.get_text()) and urlParsed.geturl() != URL:
            logger.debug(f"No '.pdf' in href, but found good link words in the text. Download site and check it!")
            findAndDownloadLinks(urlParsed.geturl(), magname)
        else:
            logger.debug(f"No PDF here and no good words. No action for this link")
    logger.debug(f"Completed 'findAndDownloadLinks' function for {magName} with URL: {URL}.")

if __name__ == "__main__":
    """
    main function. Creates the magazine config file if not present, loads it and commences the program otherwise.
    """
    logger.info("Commencing main function")
    magUrls = ""
    #If magazine definitions file exists, load it. Otherwise make one
    if not magDefsFile.exists():
        logger.warning(f"Magazine definitions file, {magDefsFile}, does not exist. Creating it")
        magUrls = {'hackspace': 'https://hackspace.raspberrypi.org/issues/','magpi': 'https://magpi.raspberrypi.org/issues/'}
        with open(magDefsFile, 'w') as outfile:
            json.dump(magUrls, outfile, indent=4)
        logger.debug(f"Finished creating magazine definitions file {magDefsFile} with data:\n{magUrls}")
    else:
        logger.debug(f"Found magazine definition file at {magDefsFile}. Loading data")
        with open(magDefsFile) as infile:
            magUrls = json.load(infile)
    logger.info(f"Established magazine definitions as:\n{str(magUrls)}")
    
    # Call the functions to start the capability.
    for magname, URL in magUrls.items():
        logger.debug(f"Commencing downloading of {magname} for URL {URL}")
        findAndDownloadLinks(URL, magname)
    
    logger.info(f"Completed main function")
