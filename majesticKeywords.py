# IMPORTS
from imports import *
from functions import *

def getKeywords(soup):
    keywordsArray = []
    keywords = soup.findAll('span',{'class':'badge thin'})
    if keywords:
        for keyword in keywords:
            keywordsArray.append(keyword.text)
    return keywordsArray

def worker(i, urlArray):

    engine = create_engine('mysql+pymysql://{0}:{1}@{2}/{3}'.format(dbUser,dbPass,hostName,db),echo=False,pool_recycle=3600)
    Base.metadata.create_all(bind=engine)
    #Session = sessionmaker(bind=engine)
    session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    for idx,websiteurl in enumerate(urlArray):
        try:
            #print("Working on {0} out of {1}".format(idx + 1, len(urlArray)))
            url = websiteurl.websiteurl

            while True:
                soup = getSoup('https://www.similarsites.com/site/' + url)
                if soup:
                    keywordsArray = getKeywords(soup)
                    if keywordsArray:
                        for keyword in keywordsArray:
                            try:
                                keyword.encode('ascii')
                                if not session.query(Keyword).filter(Keyword.keyword == keyword).count():
                                    session.add(Keyword(keyword=keyword))
                                    session.commit()
                                    session.close()
                            except UnicodeEncodeError:
                                pass
                    print(url + ' DONE')        
                    break

            # UPDATE websiteurl IN DB WHEN DONE
            row = session.query(MajesticUrl).filter(MajesticUrl.websiteurl == url).first()
            row.lastscraped = datetime.utcnow()
            session.commit()
            session.close()
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
        urls = session.query(MajesticUrl).filter(MajesticUrl.lastscraped == None).limit(10000).all()
        session.close()
        print('GOT URLS')

        numProcesses = 10
        urlArrays = numpy.array_split(numpy.array(urls),numProcesses)

        # MULTIPROCESSING
        for i in range(numProcesses):
            p = multiprocessing.Process(target=worker,args=(i, urlArrays[i]))
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
