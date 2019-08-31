import requests
import time
import selenium
count = 1
while True:
    try:
        requests.get("http://www.dh935.com/?00718-011204").text
        count += 1
    except:
        time.sleep(2)
