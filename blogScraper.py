# IMPORTS
from imports import *

# FUNCTIONS
def getkeywords():
    cursor.execute("SELECT * FROM keywords where lastscraped IS null")
    keywordNums = list(cursor)
    print("# of keywords to collect: " + str(len(keywordNums)))
    return(keywordNums)

def getProxies():
    proxyList = []
    async def show(proxies):
        while True:
            proxy = await proxies.get()
            if proxy is None:
                break
            print('Found proxy: %s' % proxy)
            strProxy = str(proxy)
            proxyList.append({'https':strProxy.split("] ",1)[1].split(">",1)[0]})

    proxies = asyncio.Queue()
    broker = Broker(proxies,timeout=1)
    tasks = asyncio.gather(
        broker.find(types=['HTTP'], limit=2),
        show(proxies))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(tasks)

    return(proxyList)

def processWebsiteInfo(rctag,keyword):
    websiteUrl = str(rctag.h2.a.get('href'))
    websiteUrl = "{0.scheme}://{0.netloc}/".format(urlsplit(websiteUrl))
    websiteUrl = re.sub(r'/$', '', websiteUrl)
    plainUrl = websiteUrl.replace('https://','').replace('http://','').replace('www.','')
    r = requests.get(websiteUrl)
    soup = BeautifulSoup(r.text, 'html.parser')
    websiteTitle = soup.title.string
    websiteTitle = str(re.sub(r'[^\x00-\x7F]+','', websiteTitle))
    websiteTitle = re.sub(r'[^A-Za-z\s]', '', websiteTitle)
    websiteTitle = websiteTitle.replace("Home ","").lstrip()
    if keyword.split(" ")[0].lower() in websiteTitle.lower():
        if soup.find('meta',{'name':'description'}):
            websiteDesc = str(soup.find('meta',{'name':'description'})).replace('<meta content="','').replace('" name="description"/>','')
        else:
            while True:
                try:
                    # proxy = random.choice(proxyList)
                    # print('Proxy using to get description: ', proxy)
                    url = "http://www.bing.com/search?q=site:" + plainUrl
                    # googler = requests.get(url, headers=myHeaders, proxies=proxy,timeout=4)
                    binger = requests.get(url, timeout=15)
                    bingSoup = BeautifulSoup(r.text, 'html.parser')
                    rctag = bingSoup.find('li', {"class":"b_algo"})
                    if rctag:
                        websiteDesc = str(rctag.find('p').get_text())
                        websiteDesc = str(re.sub(r'[^\x00-\x7F]+','', websiteDesc))
                        websiteDesc = re.sub(r'[^A-Za-z\s]', '', websiteDesc.lstrip())
                        break
                except:
                    pass
        # get page info
        links = soup.find_all('a')
        siteUrlDict = {'contactUrl':'', 'aboutUrl':''}
        socialUrlDict = {'facebookUrl':'', 'linkedinUrl':'', 'twitterUrl':'', 'pinterestUrl':'', 'youtubeUrl':'', 'instagramUrl':'', 'googleplusUrl':''}
        phone = ''
        email = ''
        for link in links:
            if link.get('href'):
                if 'contact' in link.get_text().lower():
                    siteUrlDict['contactUrl'] = link.get('href')
                    if websiteUrl not in siteUrlDict['contactUrl']:
                        siteUrlDict['contactUrl'] = websiteUrl + link.get('href')
                elif 'about' in link.get_text().lower() and 'us' in link.get_text().lower():
                    siteUrlDict['aboutUrl'] = link.get('href')
                    if websiteUrl not in siteUrlDict['aboutUrl']:
                        siteUrlDict['aboutUrl'] = websiteUrl + link.get('href')
                elif 'facebook.com' in link.get('href').lower():
                    socialUrlDict['facebookUrl'] = link.get('href')
                elif 'linkedin.com' in link.get('href').lower():
                    socialUrlDict['linkedinUrl'] = link.get('href')
                elif 'twitter.com' in link.get('href').lower():
                    socialUrlDict['twitterUrl'] = link.get('href')
                elif 'pinterest.com' in link.get('href').lower():
                    socialUrlDict['pinterestUrl'] = link.get('href')
                elif 'youtube.com' in link.get('href').lower():
                    socialUrlDict['youtubeUrl'] = link.get('href')
                elif 'instagram.com' in link.get('href').lower():
                    socialUrlDict['instagramUrl'] = link.get('href')
                elif 'plus.google.com' in link.get('href').lower():
                    socialUrlDict['googleplusUrl'] = link.get('href')
        for key, value in socialUrlDict.items():
            if not value:
                while True:
                    try:
                        # proxy = random.choice(proxyList)
                        # print('Proxy using to get description: ', proxy)
                        url = "http://www.bing.com/search?q=site:" + key.replace('Url','') + '.com%20' + plainUrl
                        # googler = requests.get(url, headers=myHeaders, proxies=proxy,timeout=15)
                        binger = requests.get(url, timeout=15)
                        bingSoup = BeautifulSoup(binger.text, 'html.parser')
                        rctag = bingSoup.find('li', {"class":"b_algo"})
                        if rctag:
                            value = str(rctag.h2.a.get('href'))
                            socialUrlDict[key] = value
                            break
                    except:
                        pass
        for key, value in siteUrlDict.items():
            if not value:
                while True:
                    try:
                        # proxy = random.choice(proxyList)
                        # print('Proxy using to get description: ', proxy)
                        url = "http://www.bing.com/search?q=site:" + plainUrl + '%20' + key.replace('Url','')
                        # googler = requests.get(url, headers=myHeaders, proxies=proxy,timeout=15)
                        binger = requests.get(url, timeout=15)
                        bingSoup = BeautifulSoup(binger.text, 'html.parser')
                        rctag = bingSoup.find('li', {"class":"b_algo"})
                        if rctag:
                            value = str(rctag.h2.a.get('href'))
                            siteUrlDict[key] = value
                            break
                    except:
                        pass
        if re.findall('\(?\d{3}[\)-]?\s?\d{3}[-\s\.]\d{4}',str(soup)):
            phone = re.findall('\(?\d{3}[\)-]?\s?\d{3}[-\s\.]\d{4}',str(soup))[0]
        if re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",str(soup)):
            email = re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",str(soup))[0]
        if not phone or not email:
            if contactUrl:
                r = requests.get(contactUrl, headers=myHeaders)
                contactSoup = BeautifulSoup(r.text, 'html.parser')
                if not phone and re.findall('\(?\d{3}[\)-]?\s?\d{3}[-\s\.]\d{4}',str(contactSoup)):
                    phone = re.findall('\(?\d{3}[\)-]?\s?\d{3}[-\s\.]\d{4}',str(contactSoup))
                if not email and re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",str(contactSoup)):
                    email = re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",str(contactSoup))[0]
        # write to db
        print("websiteurl: " + websiteUrl)
        print("websitetitle: " + websiteTitle)
        print("websitedescription: " + websiteDesc)
        print("keywordusedtofind: " + keyword)
        print("contactUrl: " + contactUrl)
        print("aboutUrl: " + aboutUrl)
        print("phone: " + phone)
        print("email: " + email)
        cursor.execute("INSERT IGNORE INTO influencers (websiteurl, websitetitle, websitedescription, keywordusedtofind, lastscraped, pagecontact, pageabout, phone, email) VALUES ('%s', '%s', '%s', '%s', %s, '%s','%s','%s','%s')" % (websiteUrl,websiteTitle,websiteDesc,keyword,'UTC_TIMESTAMP()',contactUrl,aboutUrl,phone,email))
        cnx.commit()
    else:
        print('keyword not in title: ' + websiteTitle)
        pass


# MAIN
if __name__ == "__main__":
    try:
        keywordNums = getkeywords()
        proxy = {'https':'83.149.70.159:13012'}
        searchNumber = 10
        for idx,keywordNum in enumerate(keywordNums):
            print("Working on {0} out of {1}".format(idx + 1, len(keywordNums)))
            keyword = keywordNum[1]
            url = "http://www.bing.com/search?q=blog%20intitle%3A\"" + keyword + '"'
            print("keyword working: " + keyword)
            while True:
                # proxy = random.choice(proxyList)
                # myHeaders = {'User-agent':ua.chrome}
                # print('Proxy using: ', proxy)
                try:
                    r = requests.get(url, headers=myHeaders, proxies=proxy, timeout=15)
                    # r = requests.get(url, timeout=15)
                    r = requests.get(url, timeout=15)
                    print(r)
                    if str(r) != '<Response [200]>':
                        continue
                except:
                    continue
                soup = BeautifulSoup(r.text, 'html.parser')
                rctags = []
                rctags = soup.findAll('li', {"class":"b_algo"})
                print('number of rctags: ' + str(len(rctags)))
                if not rctags:
                    continue
                for rctag in rctags:
                    processWebsiteInfo(rctag,keyword)
                cursor.execute("UPDATE keywords SET lastscraped=%s WHERE id='%s'" % ('UTC_TIMESTAMP()',keywordNum[0]))
                cnx.commit()
                break

        # stop after 1
                break
        cnx.close()
    except Exception as err:
        logging.error(err)
        print(err)
        print(traceback.format_exc())
    finally:
        print('hit finally')
        if cnx:
            cnx.close()
