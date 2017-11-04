# IMPORTS
from imports import *

# FUNCTIONS
def getkeywords():
    cursor.execute("SELECT * FROM keywords where lastscraped IS null")
    keywordNums = list(cursor)
    print("# of keywords to collect: " + str(len(keywordNums)))
    return(keywordNums)

def getHeader():
    UserAgentCSV = open(path + '/UserAgent.csv', 'r')
    UserAgentList = csv.reader(UserAgentCSV)
    UserAgentList = [row for row in UserAgentList]
    UserAgentList = [l[0] for l in UserAgentList]
    random.shuffle(UserAgentList)
    return {'User-Agent': random.choice(UserAgentList)}

def processWebsiteInfo(rctag,keyword,proxy,header,pp):
    siteInfoDict = {'websiteUrl':'','websiteTitle':'','websiteDesc':'','facebookUrl':'', 'linkedinUrl':'', 'twitterUrl':'', 'pinterestUrl':'', 'youtubeUrl':'', 'instagramUrl':'', 'googleplusUrl':'','contactUrl':'','aboutUrl':'','phone':'','email':''}

    ## GET BASIC SITE INFO - URL, TITLE, DESC
    handle = ''
    websiteUrl = str(rctag.h2.a.get('href'))
    websiteUrl = "{0.scheme}://{0.netloc}/".format(urlsplit(websiteUrl))
    siteInfoDict['websiteUrl'] = re.sub(r'/$', '', websiteUrl)
    plainUrl = siteInfoDict['websiteUrl'].replace('https://','').replace('http://','').replace('www.','')
    print('______________________________')
    print('Work on url: ' + plainUrl)
    r = requests.get(siteInfoDict['websiteUrl'], headers=header, timeout=100)
    soup = BeautifulSoup(r.text, 'html.parser')
    websiteTitle = soup.title.string
    websiteTitle = str(re.sub(r'[^\x00-\x7F]+','', websiteTitle))
    websiteTitle = re.sub(r'[^A-Za-z\s]', '', websiteTitle)
    siteInfoDict['websiteTitle'] = websiteTitle.replace("Home ","").lstrip()
    if not (keyword.split(" ")[0].lower() in websiteTitle.lower()):
        return False
    if soup.find('meta',{'name':'description'}):
        siteInfoDict['websiteDesc'] = str(soup.find('meta',{'name':'description'})).replace('<meta content="','').replace('" name="description"/>','')
    else:
        url = "http://www.bing.com/search?q=site:" + plainUrl
        r = requests.get(url, timeout=100)
        bingSoup = BeautifulSoup(r.text, 'html.parser')
        rctag = bingSoup.find('li', {"class":"b_algo"})
        if rctag:
            websiteDesc = str(rctag.find('p').get_text())
            websiteDesc = str(re.sub(r'[^\x00-\x7F]+','', websiteDesc))
            siteInfoDict['websiteDesc'] = re.sub(r'[^A-Za-z\s]', '', websiteDesc.lstrip())
            # break
        else:
            header = getHeader()
    ## CHECK SITE FOR LINKS
    links = soup.find_all('a')
    for link in links:
        if link.get('href'):
            if 'contact' in link.get_text().lower():
                siteInfoDict['contactUrl'] = link.get('href')
                if plainUrl not in siteInfoDict['contactUrl']:
                    siteInfoDict['contactUrl'] = websiteUrl + contactUrl
            elif 'about' in link.get('href').lower():
                siteInfoDict['aboutUrl'] = link.get('href')
                if plainUrl not in siteInfoDict['aboutUrl']:
                    siteInfoDict['aboutUrl'] = websiteUrl + aboutUrl
            elif 'facebook.com' in link.get('href').lower():
                siteInfoDict['facebookUrl'] = link.get('href')
            elif 'linkedin.com' in link.get('href').lower():
                siteInfoDict['linkedinUrl'] = link.get('href')
            elif 'twitter.com' in link.get('href').lower():
                siteInfoDict['twitterUrl'] = link.get('href')
            elif 'pinterest.com' in link.get('href').lower():
                siteInfoDict['pinterestUrl'] = link.get('href')
            elif 'youtube.com' in link.get('href').lower():
                siteInfoDict['youtubeUrl'] = link.get('href')
            elif 'instagram.com' in link.get('href').lower():
                siteInfoDict['instagramUrl'] = link.get('href')
            elif 'plus.google.com' in link.get('href').lower():
                siteInfoDict['googleplusUrl'] = link.get('href')
    print('Everything found on the site:')
    pp.pprint(siteInfoDict)

    # FIND CONTACT & ABOUT PAGE
    if not siteInfoDict['contactUrl']:
        url = "https://www.bing.com/search?q=site%3A" + plainUrl + '+' + 'contact'
        r = requests.get(url, proxies=proxy, headers=header, timeout=100)
        soup = BeautifulSoup(r.text, 'html.parser')
        rctags = soup.findAll('li', {"class":"b_algo"})
        if rctags:
            for rctag in rctags:
                url = str(rctag.h2.a.get('href'))
                if 'contact' in url:
                    siteInfoDict['contactUrl'] = url
                    break
            # break
        else:
            header = getHeader()
    if not siteInfoDict['aboutUrl']:
        url = "https://www.bing.com/search?q=site%3A" + plainUrl + '+' + 'about'
        r = requests.get(url, proxies=proxy, headers=header, timeout=100)
        soup = BeautifulSoup(r.text, 'html.parser')
        rctags = soup.findAll('li', {"class":"b_algo"})
        if rctags:
            for rctag in rctags:
                url = str(rctag.h2.a.get('href'))
                if 'about' in url:
                    siteInfoDict['aboutUrl'] = url
                    break
            # break
        else:
            header = getHeader()

    # GET PHONE & EMAIL
    if re.findall('\(?\d{3}[\)-]?\s?\d{3}[-\s\.]\d{4}',str(soup)):
        siteInfoDict['phone'] = re.findall('\(?\d{3}[\)-]?\s?\d{3}[-\s\.]\d{4}',str(soup))[0]
    if re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",str(soup)):
        siteInfoDict['email'] = re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",str(soup))[0]
    if not siteInfoDict['phone'] or not siteInfoDict['email'] and siteInfoDict['contactUrl']:
        r = requests.get(siteInfoDict['contactUrl'], headers=header)
        contactSoup = BeautifulSoup(r.text, 'html.parser')
        if not siteInfoDict['phone'] and re.findall('\(?\d{3}[\)-]?\s?\d{3}[-\s\.]\d{4}',str(contactSoup)):
            siteInfoDict['phone'] = re.findall('\(?\d{3}[\)-]?\s?\d{3}[-\s\.]\d{4}',str(contactSoup))
        if not siteInfoDict['email'] and re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",str(contactSoup)):
            siteInfoDict['email'] = re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",str(contactSoup))[0]
    genEmail = False
    a = ['info@','admin@','contact@','contact@','email.com','myUser']
    if any(x in siteInfoDict['email'] for x in a):
        genEmail = True
    # GET SOCIAL MEDIA
    if not siteInfoDict['youtubeUrl']:
        url = "http://www.bing.com/search?q=site:youtube.com/user+" + plainUrl
        r = requests.get(url, timeout=100, proxies=proxy,headers=header)
        soup = BeautifulSoup(r.text, 'html.parser')
        rctags = soup.findAll('li', {"class":"b_algo"})
        if rctags:
            for rctag in rctags:
                url = str(rctag.h2.a.get('href'))
                url = re.sub(r'/$', '', url)
                aboutUrl = url + '/about'
                r = requests.get(aboutUrl, timeout=100, proxies=proxy)
                soup = BeautifulSoup(r.text, 'html.parser')
                if plainUrl in str(soup):
                    siteInfoDict['youtubeUrl'] = url
                    break
            # break
    if siteInfoDict['youtubeUrl']:
        aboutUrl = siteInfoDict['youtubeUrl'] + '/about'
        r = requests.get(aboutUrl, timeout=15, proxies=proxy, headers=header)
        soup = BeautifulSoup(r.text, 'html.parser')
        socialLinks = soup.findAll('a', {"class":"about-channel-link "})
        if socialLinks:
            for link in socialLinks:
                if 'facebook.com' in link.get('href').lower():
                    siteInfoDict['facebookUrl'] = link.get('href')
                elif 'linkedin.com' in link.get('href').lower():
                    siteInfoDict['linkedinUrl'] = link.get('href')
                elif 'twitter.com' in link.get('href').lower():
                    siteInfoDict['twitterUrl'] = link.get('href')
                elif 'pinterest.com' in link.get('href').lower():
                    siteInfoDict['pinterestUrl'] = link.get('href')
                elif 'instagram.com' in link.get('href').lower():
                    siteInfoDict['instagramUrl'] = link.get('href')
                elif 'plus.google.com' in link.get('href').lower():
                    siteInfoDict['googleplusUrl'] = link.get('href')
            # break
    if not siteInfoDict['facebookUrl']:
        url = "http://www.bing.com/search?q=site:facebook.com+" + plainUrl
        r = requests.get(url, timeout=100, proxies=proxy,headers=header)
        soup = BeautifulSoup(r.text, 'html.parser')
        rctags = soup.findAll('li', {"class":"b_algo"})
        for rctag in rctags:
            fbUrl = str(rctag.h2.a.get('href'))
            print('fbUrl working on: ' + fbUrl)
            if not ('/posts' in fbUrl or '/videos' in fbUrl or '/about' in fbUrl):
                r = requests.get(fbUrl, timeout=100, proxies=proxy,headers=header)
                soup = BeautifulSoup(r.text, 'html.parser')
                if 'Security Check Required' in str(soup):
                    break
                    # continue
                contentBox = soup.find('div', {"id":"content_container"})
                if contentBox:
                    num = 0
                    for idx,desc in enumerate(list(contentBox.div.descendants)):
                        if 'About' in desc and 'span' in str(desc):
                            num = idx
                    if num:
                        mainBox = list(contentBox.div.descendants)[num].parent.parent
                        if plainUrl in str(mainBox):
                            siteInfoDict['facebookUrl'] = fbUrl
                            break
        # break
    if siteInfoDict['facebookUrl']:
        if genEmail or not (siteInfoDict['phone'] or siteInfoDict['email']):
            handle = urlsplit(siteInfoDict['facebookUrl']).path.replace('/','')
            aboutFbUrl = 'https://www.facebook.com/pg/' + handle +'/about/?ref=page_internal'
            r = requests.get(aboutFbUrl, timeout=100, proxies=proxy,headers=header)
            soup = BeautifulSoup(r.text, 'html.parser')
            num = 0
            for idx,desc in enumerate(list(soup.descendants)):
                if 'CONTACT INFO' in desc:
                    num = idx
            if num:
                contactBox = list(soup.descendants)[num].parent.parent.parent
                if not siteInfoDict['phone']:
                    if re.findall('Call \(?\d{3}[\)-]?\s?\d{3}[-\s\.]?\d{4}',str(contactBox)):
                        phone = re.findall('Call \(?\d{3}[\)-]?\s?\d{3}[-\s\.]?\d{4}',str(contactBox))[0]
                        siteInfoDict['phone'] = phone.replace('Call ','')
                if not siteInfoDict['email'] or genEmail:
                    if re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",str(contactBox)):
                        siteInfoDict['email'] = re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",str(contactBox))[0]
    if not siteInfoDict['twitterUrl']:
        url = "http://www.bing.com/search?q=site:twitter.com+" + plainUrl
        r = requests.get(url, timeout=100, proxies=proxy, headers=header)
        soup = BeautifulSoup(r.text, 'html.parser')
        rctags = soup.findAll('li', {"class":"b_algo"})
        for rctag in rctags:
            twitterUrl = str(rctag.h2.a.get('href'))
            if not ('/status' in twitterUrl):
                r = requests.get(twitterUrl, timeout=100, proxies=proxy,headers=header)
                soup = BeautifulSoup(r.text, 'html.parser')
                urlFound = soup.findAll('div', {"class":"ProfileHeaderCard-url "})[0].a.get('href')
                r = requests.get(urlFound, timeout=100, proxies=proxy,headers=header)
                if plainUrl in r.headers['Access-Control-Allow-Origin']:
                    siteInfoDict['twitterUrl'] = r.headers['Access-Control-Allow-Origin']
                    break
        # break
    if not siteInfoDict['pinterestUrl']:
        url = "http://www.bing.com/search?q=site:pinterest.com+" + plainUrl
        r = requests.get(url, timeout=100, proxies=proxy,headers=header)
        soup = BeautifulSoup(r.text, 'html.parser')
        rctags = soup.findAll('li', {"class":"b_algo"})
        for rctag in rctags:
            pinUrl = str(rctag.h2.a.get('href'))
            if not ('/pin' in pinUrl or '/explore' in pinUrl):
                r = requests.get(pinUrl, timeout=100, proxies=proxy,headers=header)
                soup = BeautifulSoup(r.text, 'html.parser')
                urlFound = soup.findAll('div', {"class":"BrioProfileHeaderWrapper"})[0].a.get('href')
                r = requests.get(urlFound, timeout=100, proxies=proxy,headers=header)
                if plainUrl in r.headers['Access-Control-Allow-Origin']:
                    siteInfoDict['pinterestUrl'] = r.headers['Access-Control-Allow-Origin']
                    break
        #break
    if not siteInfoDict['instagramUrl']:
        rctags = []
        if handle:
            for item in [plainUrl,handle]:
                url = "http://www.bing.com/search?q=site:instagram.com+" + item
                r = requests.get(url, timeout=100, proxies=proxy,headers=header)
                soup = BeautifulSoup(r.text, 'html.parser')
                rctags += soup.findAll('li', {"class":"b_algo"})
        else:
            url = "http://www.bing.com/search?q=site:instagram.com+" + plainUrl
            r = requests.get(url, timeout=100, proxies=proxy,headers=header)
            soup = BeautifulSoup(r.text, 'html.parser')
            rctags += soup.findAll('li', {"class":"b_algo"})
        for rctag in rctags:
            instaUrl = str(rctag.h2.a.get('href'))
            if not ('instagram.com/p/' in instaUrl):
                r = requests.get(instaUrl, timeout=100, proxies=proxy,headers=header)
                soup = BeautifulSoup(r.text, 'html.parser')
                if plainUrl in str(soup):
                    siteInfoDict['instagramUrl'] = instaUrl
                    break
        # break
    if not siteInfoDict['linkedinUrl']:
        url = "http://www.bing.com/search?q=site:linkedin.com/company+" + plainUrl
        r = requests.get(url, timeout=100, proxies=proxy,headers=header)
        soup = BeautifulSoup(r.text, 'html.parser')
        rctag = soup.find('li', {"class":"b_algo"})
        linkedUrl = str(rctag.h2.a.get('href'))
        r = requests.get(linkedUrl, timeout=100, proxies=proxy,headers=header)
        soup = BeautifulSoup(r.text, 'html.parser')
        if plainUrl in str(soup):
            siteInfoDict['linkedUrl'] = linkedUrl
    for key, value in siteInfoDict.items():
        if siteInfoDict[key]:
            if 'Url' in key:
                if 'http' not in value:
                    value = value.replace('//','')
                    siteInfoDict[key] = 'http://' + value
    print('Total found:')
    pp.pprint(siteInfoDict)

    cursor.execute("INSERT IGNORE INTO influencers (websiteurl, websitetitle, websitedescription, keywordusedtofind, lastscraped, pagecontact, pageabout, phone, email, facebook, twitter, pinterest, youtube, instagram, linkedin, googleplus) VALUES ('%s', '%s', '%s', '%s', %s, '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (siteInfoDict['websiteUrl'],siteInfoDict['websiteTitle'],siteInfoDict['websiteDesc'],keyword,'UTC_TIMESTAMP()',siteInfoDict['contactUrl'],siteInfoDict['aboutUrl'],siteInfoDict['phone'],siteInfoDict['email'],siteInfoDict['facebookUrl'],siteInfoDict['twitterUrl'],siteInfoDict['pinterestUrl'],siteInfoDict['youtubeUrl'],siteInfoDict['instagramUrl'],siteInfoDict['linkedinUrl'],siteInfoDict['googleplusUrl']))
    cnx.commit()


# MAIN
if __name__ == "__main__":
    try:
        keywords = getkeywords()
        proxy = {'https': '108.59.14.203:13010', 'http': '108.59.14.203:13010'}
        pp = pprint.PrettyPrinter(indent=4)
        for idx,keywords in enumerate(keywords):
            print("Working on {0} out of {1}".format(idx + 1, len(keywords)))
            keyword = keywords[1]
            url = "http://www.bing.com/search?q=blog+intitle%3A\"" + keyword + '"'
            print("keyword working: " + keyword)
            while True:
                try:
                    header = getHeader()
                    r = requests.get(url, proxies=proxy, headers=header, timeout=100)
                    if str(r) != '<Response [200]>':
                        continue
                except:
                    continue
                soup = BeautifulSoup(r.text, 'html.parser')
                rctags = soup.findAll('li', {"class":"b_algo"})
                if not rctags:
                    continue
                for rctag in rctags:
                    processWebsiteInfo(rctag,keyword,proxy,header,pp)
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




f = urllib.request.urlopen(urllib.request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36’}))
