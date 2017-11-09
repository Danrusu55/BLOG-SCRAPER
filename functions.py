from imports import *

# FUNCTIONS

def getkeywords():
    cursor.execute("SELECT keyword FROM keywords where lastscraped IS null")
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

def getSoup(url,opt=0):
    while True:
        try:
            print('url working: ', url)
            if not re.findall('.\.[a-zA-Z]+',url):
                print('url no extension: ', url)
                return False
            header = getHeader()
            data = None
            req = urllib.request.Request(url, data, header)
            f = urllib.request.urlopen(req, timeout=5)
            if f.status != 200:
                continue
            if opt:
                return f
            soup = BeautifulSoup(f.read(), 'html.parser')
            if ('redirecting' or 'security') in str(soup.title):
                continue
            if 'bing' in url:
                if not soup.find('li', {"class":"b_algo"}):
                    continue
            return soup
        except Exception as err:
            print('----------Error with conn:------')
            print(err)
            if '404' in str(err):
                break
            elif 'unknown url type' in str(err):
                break
            else:
                continue

def cleanLink(link, websiteUrl=''):
    if ('contact' or 'about') in link:
        if urlsplit(link).netloc:
            if plainUrl in link.netloc:
                return(link)
            else:
                return('')
        else:
            urlPath = re.sub('^/+', '', urlPath)
            url = websiteUrl + '/' + urlPath
            return(urlPath)
    elif 'facebook' in link:
        temp = urlsplit(link).path
        urlPath = re.match(r'^/[^/]+', temp).group()
        return('http://facebook.com' + urlPath)
    elif 'twitter' in link:
        temp = urlsplit(link).path
        urlPath = re.match(r'^/[^/]+', temp).group()
        return('http://twitter.com' + urlPath)
    elif 'pinterest' in link:
        temp = urlsplit(link).path
        urlPath = re.match(r'^/[^/]+', temp).group()
        return('http://pinterest.com' + urlPath)
    elif 'instagram' in link:
        temp = urlsplit(link).path
        urlPath = re.match(r'^/[^/]+', temp).group()
        return('http://instagram.com' + urlPath)
    elif 'plus.google' in link:
        temp = urlsplit(link).path
        urlPath = re.match(r'/[^/]{6,30}', temp).group()
        return('http://plus.google.com' + urlPath)
    elif 'linkedin' in link:
        temp = urlsplit(link).path
        urlPath = re.match(r'/(in|company)\/[^/]+', temp).group()
        return('http://linkedin.com' + urlPath)
    elif 'youtube' in link:
        temp = urlsplit(link).path
        urlPath = re.match(r'/(user|channel)\/[^/]+', temp).group()
        return('http://youtube.com' + urlPath)

def cleanWebsiteUrl(rctag):
    websiteUrl = str(rctag.h2.a.get('href'))
    websiteUrl = "{0.scheme}://{0.netloc}/".format(urlsplit(websiteUrl))
    return(re.sub(r'/$', '', websiteUrl))

def cleanText(text):
    text = str(re.sub(r'[^\x00-\x7F]+','', text))
    text = re.sub(r'[^A-Za-z0-9\s]', '', text)
    return(text)

def getSearchLinksGoogle(soup):
    linksArray = []
    rctags = soup.findAll('div', {"class":"g"})
    ignoreList = ['top ','list','best']
    if rctags:
        for rctag in rctags:
            siteTitle = rctag.h3.get_text().lower()
            s = str(rctag.h3.a.get('href')).replace('/url?q=','')
            url = "{0.scheme}://{0.netloc}/".format(urlsplit(s))
            url = re.sub(r'/$', '', url).replace('www.','')
            if not any(ext in siteTitle for ext in ignoreList) and not any(ext in url for ext in ignoreSites) and not (url in linksArray) and not (re.search(r'^\d',siteTitle)):
                if 'blog' in urlsplit(s).path:
                    linksArray.append([url,s])
                else:
                    linksArray.append([url,''])
        return linksArray
    else:
        return False

def getSearchLinks(soup):
    linksArray = []
    rctags = soup.findAll('li', {"class":"b_algo"})
    if rctags:
        for rctag in rctags:
            url = str(rctag.h2.a.get('href'))
            url = re.sub(r'/$', '', url)
            linksArray.append(url)
        return linksArray
    else:
        return False

def getSocialLinks(siteInfoDict,plainUrl):
    if not siteInfoDict['youtubeUrl']:
        print('--working: ', 'youtubeUrl')
        url = "http://www.bing.com/search?q=site:youtube.com/user+" + plainUrl
        soup = getSoup(url)
        searchLinks = getSearchLinks(soup)
        if searchLinks:
            for url in searchLinks:
                aboutUrl = url + '/about'
                soup = getSoup(aboutUrl)
                if plainUrl in str(soup):
                    siteInfoDict['youtubeUrl'] = url
                    break
    if siteInfoDict['youtubeUrl']:
        aboutUrl = siteInfoDict['youtubeUrl'] + '/about'
        soup = getSoup(aboutUrl)
        socialLinks = soup.findAll('a', {"class":"about-channel-link "})
        if socialLinks:
            for link in socialLinks:
                link = link.get('href').lower()
                if 'facebook.com' in link:
                    siteInfoDict['facebookUrl'] = link
                elif 'linkedin.com' in link:
                    siteInfoDict['linkedinUrl'] = link
                elif 'twitter.com' in link:
                    siteInfoDict['twitterUrl'] = link
                elif 'pinterest.com' in link:
                    siteInfoDict['pinterestUrl'] = link
                elif 'instagram.com' in link:
                    siteInfoDict['instagramUrl'] = link
                elif 'plus.google.com' in link:
                    siteInfoDict['googleplusUrl'] = link
    if not siteInfoDict['facebookUrl']:
        print('--working: ', 'facebookUrl')
        url = "http://www.bing.com/search?q=site:facebook.com+" + plainUrl
        soup = getSoup(url)
        searchLinks = getSearchLinks(soup)
        if searchLinks:
            for url in searchLinks:
                if not ('/posts' in fbUrl or '/videos' in fbUrl or '/about' in url):
                    soup = getSoup(url)
                    contentBox = soup.find('div', {"id":"content_container"})
                    if contentBox:
                        num = 0
                        for idx,desc in enumerate(list(contentBox.div.descendants)):
                            if 'About' in desc and 'span' in str(desc):
                                num = idx
                        if num:
                            mainBox = list(contentBox.div.descendants)[num].parent.parent
                            if plainUrl in str(mainBox):
                                siteInfoDict['facebookUrl'] = url
                                break
    if siteInfoDict['facebookUrl']:
        if genEmail or not (siteInfoDict['phone'] or siteInfoDict['email']):
            handle = urlsplit(siteInfoDict['facebookUrl']).path.replace('/','')
            aboutFbUrl = 'https://www.facebook.com/pg/' + handle +'/about/?ref=page_internal'
            soup = getSoup(aboutFbUrl)
            num = 0
            for idx,desc in enumerate(list(soup.descendants)):
                if 'CONTACT INFO' in desc:
                    num = idx
            if num:
                contactBox = str(list(soup.descendants)[num].parent.parent.parent)
                if not siteInfoDict['phone']:
                    if re.findall('Call \(?\d{3}[\)-]?\s?\d{3}[-\s\.]?\d{4}',contactBox):
                        phone = re.findall('Call \(?\d{3}[\)-]?\s?\d{3}[-\s\.]?\d{4}',contactBox)[0]
                        siteInfoDict['phone'] = phone.replace('Call ','')
                if not siteInfoDict['email'] or genEmail:
                    if re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",contactBox):
                        siteInfoDict['email'] = re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",contactBox)[0]
                if 'twitter.com' in contactBox:
                    siteInfoDict['twitterUrl'] = re.findall('twitter.com/[a-zA-z0-9]+',contactBox)
                elif 'instagram.com' in contactBox:
                    siteInfoDict['instagramUrl'] = re.findall('instagram.com/[a-zA-z0-9]+',contactBox)
                elif 'pinterest.com' in contactBox:
                    siteInfoDict['pinterestUrl'] = re.findall('pinterest.com/[a-zA-z0-9]+',contactBox)
                elif 'linkedin.com' in contactBox:
                    siteInfoDict['linkedinUrl'] = re.findall('linkedin.com/[a-zA-z0-9]+',contactBox)
    if not siteInfoDict['twitterUrl']:
        print('--working: ', 'twitterUrl')
        url = "http://www.bing.com/search?q=site:twitter.com+" + plainUrl
        soup = getSoup(url)
        searchLinks = getSearchLinks(soup)
        if searchLinks:
            for url in searchLinks:
                soup = getSoup(url)
                if soup:
                    if soup.findAll('div', {"class":"ProfileHeaderCard-url "}):
                        urlFound = soup.findAll('div', {"class":"ProfileHeaderCard-url "})[0].a.get('href')
                        f = getSoup(urlFound,opt=1)
                        if f:
                            if plainUrl in f.geturl():
                                siteInfoDict['twitterUrl'] = f.geturl()
                                break
    if not siteInfoDict['pinterestUrl']:
        print('--working: ', 'pinterestUrl')
        url = "http://www.bing.com/search?q=site:pinterest.com+" + plainUrl
        soup = getSoup(url)
        searchLinks = getSearchLinks(soup)
        if searchLinks:
            for url in searchLinks:
                if not ('/pin' in url or '/explore' in url):
                    soup = getSoup(url)
                    if soup:
                        if soup.findAll('div', {"class":"BrioProfileHeaderWrapper"}):
                            urlFound = soup.findAll('div', {"class":"BrioProfileHeaderWrapper"})[0].a.get('href')
                            if urlFound:
                                if ('http' or 'www.') in urlFound:
                                    f = getSoup(urlFound,opt=1)
                                    if not f:
                                        continue
                                    if plainUrl in f.geturl():
                                        siteInfoDict['pinterestUrl'] = f.geturl()
                                        break
    if not siteInfoDict['instagramUrl']:
        print('--working: ', 'instagramUrl')
        rctags = []
        searchLinks = []
        url = "http://www.bing.com/search?q=site:instagram.com+" + plainUrl
        soup = getSoup(url)
        searchLinks = getSearchLinks(soup)
        if handle:
            url = "http://www.bing.com/search?q=site:instagram.com+" + plainUrl
            soup = getSoup(url)
            searchLinks += getSearchLinks(soup)
        if searchLinks:
            for url in searchLinks:
                if not ('instagram.com/p/' in instaUrl):
                    soup = getSoup(url)
                    if not soup:
                        continue
                    if plainUrl in str(soup):
                        siteInfoDict['instagramUrl'] = url
                        break
    if not siteInfoDict['linkedinUrl']:
        print('--working: ', 'linkedinUrl')
        url = "http://www.bing.com/search?q=site:linkedin.com/company+" + plainUrl
        soup = getSoup(url)
        rctag = soup.find('li', {"class":"b_algo"})
        if rctag:
            linkedUrl = str(rctag.h2.a.get('href'))
            siteInfoDict['linkedUrl'] = linkedUrl
    return(siteInfoDict)

def getPhoneEmail(siteInfoDict,mainSiteSoup):
    if re.findall('\(?\d{3}[\)-]?\s?\d{3}[-\s\.]\d{4}',str(mainSiteSoup)):
        siteInfoDict['phone'] = re.findall('\(?\d{3}[\)-]?\s?\d{3}[-\s\.]\d{4}',str(mainSiteSoup))[0]
    if re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",str(mainSiteSoup)):
        siteInfoDict['email'] = re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",str(mainSiteSoup))[0]
    if not siteInfoDict['phone'] or not siteInfoDict['email'] and siteInfoDict['contactUrl']:
        soup = getSoup(siteInfoDict['contactUrl'])
        if not siteInfoDict['phone'] and re.findall('\(?\d{3}[\)-]?\s?\d{3}[-\s\.]\d{4}',str(soup)):
            siteInfoDict['phone'] = re.findall('\(?\d{3}[\)-]?\s?\d{3}[-\s\.]\d{4}',str(soup))
        if not siteInfoDict['email'] and re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",str(soup)):
            siteInfoDict['email'] = re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",str(soup))[0]
    genEmail = False
    a = ['info@','admin@','contact@','contact@','email.com','myUser']
    if any(x in siteInfoDict['email'] for x in a):
        genEmail = True
    return(genEmail, siteInfoDict)

def getContactAbout(siteInfoDict):
    if not siteInfoDict['contactUrl']:
        print('--working: ', 'contactUrl')
        url = "https://www.bing.com/search?q=site%3A" + plainUrl + '+' + 'contact'
        soup = getSoup(url)
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
        print('--working: ', 'aboutUrl')
        url = "https://www.bing.com/search?q=site%3A" + plainUrl + '+' + 'about'
        soup = getSoup(url)
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
    return(siteInfoDict)

def getOnsiteLinks(siteInfoDict,mainSiteSoup):
    links = mainSiteSoup.find_all('a')
    for link in links:
        link = link.get('href').lower()
        if link:
            link = re.sub(r'^/{2,10}','/', link)
            if not siteInfoDict['contactUrl']:
                if 'contact' in link:
                    siteInfoDict['contactUrl'] = cleanLink(link, siteInfoDict['websiteUrl'])
            if not siteInfoDict['aboutUrl']:
                if 'about' in link:
                    siteInfoDict['aboutUrl'] = cleanLink(link, siteInfoDict['websiteUrl'])
            elif 'facebook.com' in link:
                siteInfoDict['facebookUrl'] = cleanLink(link)
            elif 'linkedin.com' in link:
                siteInfoDict['linkedinUrl'] = cleanLink(link)
            elif 'twitter.com' in link:
                siteInfoDict['twitterUrl'] = cleanLink(link)
            elif 'pinterest.com' in link:
                siteInfoDict['pinterestUrl'] = cleanLink(link)
            elif 'youtube.com' in link:
                siteInfoDict['youtubeUrl'] = cleanLink(link)
            elif 'instagram.com' in link:
                siteInfoDict['instagramUrl'] = cleanLink(link)
            elif 'plus.google.com' in link:
                siteInfoDict['googleplusUrl'] = cleanLink(link)
    return(siteInfoDict)

def getDesc(siteInfoDict):
    if mainSiteSoup.find('meta',{'name':'description'}):
        data = str(mainSiteSoup.find('meta',{'name':'description'})).replace('<meta content="','').replace('" name="description"/>','')
        siteInfoDict['websiteDesc'] = (data[:75] + '..') if len(data) > 75 else data
    else:
        url = "http://www.bing.com/search?q=site:" + plainUrl
        soup = getSoup(url)
        rctag = soup.find('li', {"class":"b_algo"})
        if rctag:
            websiteDesc = str(rctag.find('p').get_text())
            data = cleanText(websiteDesc)
            siteInfoDict['websiteDesc'] = (data[:75] + '..') if len(data) > 75 else data
    return(siteInfoDict)

def getTitle(siteInfoDict):
    mainSiteSoup = getSoup(siteInfoDict['websiteUrl'])
    siteInfoDict['websiteTitle'] = cleanText(mainSiteSoup.title.string).replace("Home ","").lstrip()
    return(siteInfoDict)

def getKeywordCount(text,keyword):
    number_of_occurences = 0
    for word in text.split():
      if word == keyword:
        number_of_occurences += 1
    return(number_of_occurences)

def processWebsiteInfo(url,blogUrl,keywordUsedToFind):
    # INITIAL TERMS
    siteInfoDict = {'websiteUrl':'','blogUrl':'','websiteTitle':'','websiteDesc':'','facebookUrl':'', 'linkedinUrl':'', 'twitterUrl':'', 'pinterestUrl':'', 'youtubeUrl':'', 'instagramUrl':'', 'googleplusUrl':'','contactUrl':'','aboutUrl':'','phone':'','email':'','keywordUsedToFind':''}
    handle = ''

    # GET WEBSITE URL
    siteInfoDict['websiteUrl'] = url
    siteInfoDict['blogUrl'] = blogUrl
    siteInfoDict['keywordUsedToFind'] = keywordUsedToFind

    plainUrl = siteInfoDict['websiteUrl'].replace('https://','').replace('http://','').replace('www.','')

    # ENSURE NOT IN db
    cursor.execute("SELECT id FROM influencers WHERE  INSTR(`websiteurl`, '{0}') > 0;".format(plainUrl))
    if list(cursor):
        return False

    # GET Title, Desc
    print('______________________________')
    print('Working on url: ' + plainUrl)
    siteInfoDict = getTitle(siteInfoDict)
    siteInfoDict = getDesc(siteInfoDict)

    # CHECK SITE FOR LINKS
    siteInfoDict = getOnsiteLinks(siteInfoDict, mainSiteSoup)
    print('Found just on site:')
    pp.pprint(siteInfoDict)

    # FIND CONTACT & ABOUT PAGE
    siteInfoDict = getContactAbout(siteInfoDict)

    # GET PHONE & EMAIL
    genEmail, siteInfoDict = getPhoneEmail(siteInfoDict,mainSiteSoup)

    # GET SOCIAL MEDIA
    siteInfoDict = getSocialLinks(siteInfoDict,plainUrl)
    print('Found in total:')
    pp.pprint(siteInfoDict)

    cursor.execute("INSERT IGNORE INTO influencers (websiteurl, websitetitle, websitedescription, keywordusedtofind, lastscraped, pagecontact, pageabout, phone, email, facebook, twitter, pinterest, youtube, instagram, linkedin, googleplus) VALUES ('%s', '%s', '%s', '%s', %s, '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (siteInfoDict['websiteUrl'],siteInfoDict['websiteTitle'],siteInfoDict['websiteDesc'],keyword,'UTC_TIMESTAMP()',siteInfoDict['contactUrl'],siteInfoDict['aboutUrl'],siteInfoDict['phone'],siteInfoDict['email'],siteInfoDict['facebookUrl'],siteInfoDict['twitterUrl'],siteInfoDict['pinterestUrl'],siteInfoDict['youtubeUrl'],siteInfoDict['instagramUrl'],siteInfoDict['linkedinUrl'],siteInfoDict['googleplusUrl']))
    cnx.commit()
