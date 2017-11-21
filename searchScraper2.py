# IMPORTS
from imports import *
from functions import *

engine = create_engine('mysql+pymysql://{0}:{1}@{2}/{3}'.format(dbUser,dbPass,hostName,db),echo=False,pool_recycle=3600)
Base.metadata.create_all(bind=engine)
Session = scoped_session(sessionmaker(bind=engine))

def getSearchLinksGoogle(soup,keyword):
    linksArray = []
    rctags = soup.findAll('div', {"class":"g"})
    ignoreList = ['top ','list','best']
    if rctags:
        for rctag in rctags:
            if rctag.h3:
                siteTitle = rctag.h3.get_text().lower()
                s = str(rctag.h3.a.get('href')).replace('/url?q=','')
                s = s.split('&')[0]
                url = "{0.scheme}://{0.netloc}/".format(urlsplit(s))
                url = re.sub(r'/$', '', url).replace('www.','')
                if not any(ext in siteTitle for ext in ignoreList) and not any(ext in url for ext in ignoreSites) and not (url in linksArray) and not (re.search(r'^\d',siteTitle)) and len(s) < 250:
                    linksArray.append([url,s])
        return linksArray
    else:
        return False

def worker(i, keywordArray):

    for idx,keyword in enumerate(keywordArray):
        try:
            Session = scoped_session(sessionmaker(bind=engine))
            print("Working on {0} out of {1}".format(idx + 1, len(keywordArray)))
            keyword = keyword.keyword

            # GET GOOGLE RESULTS FOR THE KEYWORDS
            print('Worker ', i, ' working on getting google results')
            searchLinks = []
            for i in range(0,1000,100):
                print('Worker ', i, ' working range: ', i)
                googleUrl = 'https://www.google.com/search?q=intitle:blog+{0}&num={1}&start={2}&sa=N&filter=0'.format(keyword.replace(' ','+'),'100',i)
                soup = getSoup(googleUrl)
                if 'did not match any documents.' in soup.get_text():
                    break
                else:
                    x = getSearchLinksGoogle(soup,keyword)
                    if x:
                        searchLinks += x

            # WORK ON THE SEARCH LINKS
            print('Worker ', i, ' working on searchlinks adding to db')
            for result in searchLinks:
                url = result[0]
                blogUrl = result[1]
                plainUrl = url.replace('https://','').replace('http://','').replace('www.','').replace('/','')
                id = ''
                id = Session.query(Website).filter(Website.websiteurl.contains(plainUrl)).all()
                if not id:
                    print('adding url: ', url, ' blog: ', blogUrl)
                    Session.add(Website(websiteurl=url,blogurl=blogUrl,keywordusedtofind=keyword))
                    Session.commit()
                    #session.remove()
            # UPDATE KEYWORD IN DB WHEN DONE
            row = Session.query(Keyword).filter(Keyword.keyword == keyword).first()
            row.lastscraped = datetime.utcnow()
            Session.commit()
            #session.remove()
        except Exception as err:
            print('Error in worker: ', err)
            print(traceback.format_exc())
            pass
    return

# MAIN
if __name__ == "__main__":
    try:
        # INITIAL VARIABLES
        jobs = []
        keywords = Session.query(Keyword).filter(Keyword.lastscraped == None).all()
        #session.remove()
        numProcesses = 10
        keywordArrays = numpy.array_split(numpy.array(keywords),numProcesses)

        # MULTIPROCESSING
        for i in range(numProcesses):
            p = multiprocessing.Process(target=worker,args=(i, keywordArrays[i]))
            jobs.append(p)
            p.start()
        for job in jobs:
            job.join()
    except Exception as err:
        logging.error(err)
        print(err)
        print(traceback.format_exc())
    finally:
        print('FINALLY: COMPLETED')
