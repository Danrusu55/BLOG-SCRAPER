from imports import *
from functions import *


# MAIN
if __name__ == "__main__":
    try:
        
        # INITIAL VARIABLES
        graph = facebook.GraphAPI(fbToken)
        keywords = session.query(Keyword).filter(Keyword.lastscrapedfacebook == None).all()

        for keyword in keywords:
            keyword = keyword.keyword
            print('--------------------------')
            print('WORKING ON KEYWORD: ', keyword)

            #RUN THE SEARCH ON THAT KEYWORD
            allPages = []
            pages = graph.request('/search?q={0}&type=page'.format(keyword.replace(' ', '%20')))
            while True:
                try:
                    print('CURRENT LENGTH OF ALLPAGES: ', len(allPages))
                    for page in pages['data']:
                        name = page['name']
                        fbId = page['id']
                        if name.encode('ascii',errors='ignore').decode('utf-8') == name:
                            exists = session.query(Website).filter(Website.fbid == fbId).all()
                            if not exists:
                                session.add(Website(fbid=fbId, keywordusedtofind=keyword)) 		
                                session.commit()
                                print('added this fb page: ', name)
                            else:
                                print('passed on: ', name)
                    nextUrl = pages['paging']['next']
                    print('getting next url: ', nextUrl)
                    pages = requests.get(nextUrl).json()
                    time.sleep(random.randint(5,100))
                except KeyError:
                    break
            row = session.query(Keyword).filter(Keyword.keyword == keyword).first()
            row.lastscrapedfacebook = datetime.utcnow()
            session.commit()
    except Exception as err:
        logging.error(err)
        print(err)
        print(traceback.format_exc())
    finally:
        session.close()
        print('FINALLY: COMPLETED')
