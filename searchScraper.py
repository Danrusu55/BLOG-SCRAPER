# IMPORTS
from imports import *
from functions import *

def worker(i, keywordArray):
    for idx,keyword in enumerate(keywordArray):
        print("Working on {0} out of {1}".format(idx + 1, len(keywordArray)))
        keyword = keyword[0]

        # GET GOOGLE RESULTS FOR THE KEYWORDS
        searchLinks = []
        for i in range(0,1000,100):
            googleUrl = 'https://www.google.com/search?q=blog+intitle:{0}&num={1}&start={2}&sa=N&filter=0'.format(keyword.replace(' ','+'),'100',i)
            soup = getSoup(googleUrl)
            if 'did not match any documents.' in soup.get_text():
                break
            else:
                searchLinks += getSearchLinksGoogle(soup)

        # WORK ON THE SEARCH LINKS
        for result in searchLinks:
            url = result[0]
            blogUrl = result[1]
            plainUrl = url.replace('https://','').replace('http://','').replace('www.','')
            cursor.execute("SELECT id FROM websitelist WHERE  INSTR(`websiteurl`, '{0}') > 0;".format(plainUrl))
            if not list(cursor):
                print('inserting: ' + plainUrl)
                cursor.execute("INSERT IGNORE INTO websiteList (websiteurl, keywordusedtofind, scrapedon, blogurl) VALUES ('%s', '%s', %s, '%s')" % (url, keyword, 'UTC_TIMESTAMP()', blogUrl))
                cnx.commit()

        # UPDATE KEYWORD IN DB WHEN DONE
        cursor.execute("UPDATE keywords SET lastscraped=%s WHERE keyword='%s'" % ('UTC_TIMESTAMP()',keyword))
        cnx.commit()
    return

# MAIN
if __name__ == "__main__":
    try:
        # INITIAL VARIABLES
        jobs = []
        keywords = getkeywords()
        keywordArrays = numpy.array_split(numpy.array(keywords),5)

        # MULTIPROCESSING
        for i in range(5):
            p = multiprocessing.Process(target=worker,args=(i, keywordArrays[i]))
            jobs.append(p)
            p.start()
        cnx.close()
    except Exception as err:
        logging.error(err)
        print(err)
        print(traceback.format_exc())
    finally:
        print('hit finally')
        if cnx:
            cnx.close()
