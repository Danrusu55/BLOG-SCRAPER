import multiprocessing, time, random

def worker(i):
    """worker function"""
    randint = random.randint(0,4)
    time.sleep(randint)
    print('Worker ', i)
    randint = random.randint(0,4)
    time.sleep(randint)
    print('Worker ', i)
 
    
    return

if __name__ == '__main__':
    jobs = []
    for i in range(5):
        p = multiprocessing.Process(target=worker,args=(i,))
        jobs.append(p)
        p.start()