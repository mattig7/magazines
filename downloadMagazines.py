#! python3
# downloadXkcd.py - Downloads the first 35 hackspace magazines.

import requests, bs4, os, logging

magUrls = {'hackspace': 'https://hackspace.raspberrypi.org/issues/','magpi': 'https://magpi.raspberrypi.org/issues/'}
for entry in magUrls.Items():
   os.makedirs(entry, exist_ok=True)

# Download the url, and find all instances of magazine download links



for issuenum in range(9,32):
   # Download the magazine.
   magUrl = url + str(issuenum) + '/pdf'
   print(f'Downloading issue {issuenum} from {magUrl}')
   res = requests.get(magUrl)
   res.raise_for_status()
   
   soup = bs4.BeautifulSoup(res.text, 'html.parser')
   magElements = soup.select('p a.c-link')
   
   if magElements == []:
      print('Could not find magazine.')
   else:
      actualMagUrl = magElements[0].get('href')
      print(f'Saving magazine from actual link {actualMagUrl}')
      
      magFile = open(os.path.join('hackspace', str(issuenum) + '.pdf'), 'wb')
      res2 = requests.get(actualMagUrl)
      res2.raise_for_status()

      for chunk in res2.iter_content(100000):
         magFile.write(chunk)
      
      magFile.close()

print('Done.')




