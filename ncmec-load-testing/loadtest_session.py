import rest
import logging
import threading
import datetime
import time
        
logging.basicConfig(level=logging.DEBUG, format="%(threadName)s:%(message)s")

def OK():
    CSI="\x1B["
    print CSI+"32;40m" + "OK" + CSI+"0m"

def ERROR():
    CSI="\x1B["
    print CSI+"31;40m" + "ERROR" + CSI+"0m"    

class LoadTestingClass(threading.Thread):
    def __init__(self):
        self.start_time = time.time()
        self.end_time = None
        self.msg = None
        threading.Thread.__init__(self)

    def run(self):
        logging.info('.')
        (resp, msg) = rest.session_v1(submitDetails=False)
        if resp == 0:
            OK()
            self.end_time = time.time()
        else:
            ERROR()
            self.msg = msg


NUM_QUERIES = 15 
REQUESTS = []

for i in range(NUM_QUERIES):
    t = LoadTestingClass()
    REQUESTS.append(t)
    t.start()

all_threads = threading.enumerate() 
while ( len(all_threads) > 1):
    logging.debug('Checking all threads are done.')
    logging.debug(threading.enumerate())
    time.sleep(1)
    all_threads = threading.enumerate()

# All threads have returned. We can now process the results.

REQUESTS_FAIL = [k for k in REQUESTS if k.end_time is None]
REQUESTS_OK = [k for k in REQUESTS if k.end_time is not None]

print "%d OK queries." % len(REQUESTS_OK)
print "%d FAIL queries." % len(REQUESTS_FAIL)


for q in REQUESTS_FAIL:
    print q.getName(), q.msg



if len(REQUESTS_OK) > 0:
    results = sorted(map(lambda x: x.end_time - x.start_time, REQUESTS_OK))
    print "Min response time: %f s." % results[0]
    print "Max response time: %f s." % results[-1]
    print "Average response time: %f s. " % (sum(results)/len(results))
    print "Median response time: %f s. " % results[len(results) / 2]
else:
    print "No stats because no OK request."

