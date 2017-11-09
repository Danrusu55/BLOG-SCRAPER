# IMPORTS
from imports import *
from functions import *

# MAIN
if __name__ == "__main__":
    with open('bestofweblist.txt','r') as inFile:
        urlList = inFile.readlines()
        for url in urlList:
            try:
                url = url.replace('\n','')
                print('________________________________')
                print('working on: ' + url)
                r = requests.get(url)
                soup = BeautifulSoup(r.text,'html.parser')
                text = soup.find('div',{'id':'Listings'}).get_text()
                text = text.replace('  ','').replace('\r','').replace('\n','')
                with open('bestofwebtext.txt','a') as outFile:
                    outFile.write(text)
            except:
                pass

