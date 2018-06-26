# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import os

headerdic = {
"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
"Accept-Encoding": "utf-8",
"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
}
headers = []
for key, val in headerdic.items():
    item = (key, val)
    headers.append(item)

httphd = urllib.request.HTTPHandler(debuglevel = 1)
httpshd = urllib.request.HTTPSHandler(debuglevel = 1)
#--- use debuglog
opener = urllib.request.build_opener(httphd, httpshd)
opener.addheaders = headers
urllib.request.install_opener(opener) # Set the defined opener as global opener

def get_test_page(url, name):
    url = url
    outfile = "./test/"+name
    try:
        webpage = opener.open(url, timeout=5)
        #--- Write webpages to html files
        fhandle = open(outfile, "wb")
        fhandle.write(webpage.read())
        fhandle.close()
        print("Get json file")
        print("URL: "+url)
    except Exception as err:
        print(err)
    

    
    
    

# testUrl = "http://www.qdaily.com/tags/tagmore/1068/1527061426.json"
# testUrl = "http://www.qdaily.com/tags/1068.html"
# get_test_page(testUrl, '1068.html')

# jsonfile = "http://www.qdaily.com/tags/tagmore/1068/1527144339.json"
# get_test_page(jsonfile, '152714439-1st.json')

# errpage = "http://www.qdaily.com/cards/53127.html"
# get_test_page(errpage, '404.html')

testUrl = "http://www.qdaily.com/articles/54077.html"
get_test_page(testUrl, 'article-54077.html')