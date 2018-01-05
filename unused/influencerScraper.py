# IMPORTS
from imports import *
from functions import *

def worker(i, websiteList):
    for idx,website in enumerate(websiteList):
            print("Working on {0} out of {1}".format(idx + 1, len(websiteList)))
            url = website[1]
            blogUrl = website[2]
            keywordUsedToFind = website[3]

            while True:
                soup = getSoup(url)
                if soup:
                    processWebsiteInfo(url,blogUrl,keywordUsedToFind)
                    cursor.execute("UPDATE keywords SET lastscraped=%s WHERE id='%s'" % ('UTC_TIMESTAMP()',keywordNum[0]))
                    cnx.commit()
                    break
        # stop after 1
                break
        cnx.close()
    return

# MAIN
if __name__ == "__main__":
    try:
        # INITIAL VARIABLES
        jobs = []
        websiteList = cursor.execute("SELECT * FROM websitelist")
        websiteArrays = numpy.array_split(numpy.array(websiteList),5)

        # MULTIPROCESSING
        for i in range(5):
            p = multiprocessing.Process(target=worker,args=(i, websiteArrays[i]))
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