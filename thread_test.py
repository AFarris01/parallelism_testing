import multiprocessing as mp
import concurrent.futures as cf
import requests
from time import time
import urllib3

# Turn off the annoying "Inescure Request" Warnings from SSL request errors
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

urlist = ['http://www.microsoft.com', 
          'http://www.microsoft.org', 
          'http://www.microsoft.net', 
          'http://www.microsoft.co.uk', 
          'http://www.microsoft.nl', 
          'http://www.microsoft.co', 
          'http://www.microsoft.dk', 
          'http://www.outlook.dk', 
          'http://www.skype.dk', 
          'http://www.live.dk', 
          'http://www.hotmail.dk', 
          'http://www.hotmail.se', 
          'http://www.microsoft.se']

def fetchURLm(url):
    """ Fetch a given URL in a unique 'browser session' and return the request.
    """
    session = requests.Session()
    return session.get(url,timeout=3,verify=False)

def fetchURL(url):
    """ Print statistics about fetching individual URLs.
        Useful for determining bounds for how long the batch may take.
    """
    startime = time()
    r = fetchURLm(url)
    contentlength = len(r.content)
    duration = time()-startime
    if r.status_code is 200:
        print(f"\tRetrieved {contentlength} bytes from {url} in {duration:.4f}s")
    else:
        print(f"\tFailed to retrieve {url}: {r.status_code}")
    return r
        
def sequenceFetch(urls,details=False):
    """ Fetch a given list of URLs serially, and print some statistics on how long it took
    """
    if details:
        fetcher=fetchURL
    else:
        fetcher=fetchURLm
    return [fetcher(url) for url in urls]

def asyncFetch(urls,details=False):
    """ Fetch a given list of URLs with a thread pool, and print some statistics on how long it took
    """
    allresults = []
    with cf.ThreadPoolExecutor() as executor:
        allresults = executor.map(fetchURLm,urls)
    return allresults

def parallelFetch(urls,details=False):
    """ Fetch a given list of URLs with a process pool, and print some statistics on how long it took
    """
    allresults = []
    with mp.Pool() as pool:
        allresults = pool.map(fetchURLm,urls)
    return allresults
    
def fetchSummarize(urls, fetcher=sequenceFetch, details=False):
    startime = time()
    allresults = fetcher(urls,details)
    totalfetched = sum([len(r.content) for r in allresults if r])
    num=len(urls)
    duration = time()-startime
    print(f"\tRetrieved a total of {totalfetched} bytes from {num} URLs in {duration:.4f}s")

    
if __name__ == '__main__':
    print("Details on proposed sequence:")
    fetchSummarize(urlist,details=True)
    
    print("Timing sequential URL requests...")
    fetchSummarize(urlist)

    print("Timing Async URL requests...")
    fetchSummarize(urlist,asyncFetch)

    print("Timing Parallel URL requests...")
    fetchSummarize(urlist,parallelFetch)
