import requests
import sys
import time

if __name__ == "__main__":
    ip = sys.argv[1]
    numRequests = int(sys.argv[2])

    start = time.time()
    for u in range(numRequests):
        user='user'+str(u)
        url = f'http://{ip}/getfeed/{user}'    
        r = requests.get(url, auth=('user', 'pass'))
        print("GET ", url, " returned status code", r.status_code)
        #print(r.text)

    end = time.time()
    tElapsed = end - start
    rps = numRequests/tElapsed
    print(f"RPS {rps:3f}")
