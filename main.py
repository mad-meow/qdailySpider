# -*- coding: utf-8 -*-
from urldb import *
from webspider import *
from mylib import *

qdailyDB = Urldb()

# 好奇心长文章爬虫
# 起始页
startUrl = 'http://www.qdaily.com/tags/1068.html'
qdailySpider = QDailyWeb(startUrl)
startDic = qdailySpider.entryWeb()

# 长文章服务端Json文件
jsonType = 'LongArticle'
def transJsUrl(jskey):
    return "http://www.qdaily.com/tags/tagmore/1068/%s.json" %(jskey)


# 解析起始页面，获得首页文章和jsonKey
startDic = qdailySpider.entryWeb()
jsonKey = startDic['lastKey']
artList = startDic['artList']
del startDic

# 处理文章列表中每个文章链接
while artList:
    art = artList.pop()
    have = qdailyDB.checkUrl(art['id'], art['type'], art['title'], art['url'])
    if (have == 0):
        store = qdailySpider.storeArticle(art['url'], art['id'])
        qdailyDB.markDoneUrl(art['url'])
    else:
        print("文章已存储")



while jsonKey:
    jsonUrl = transJsUrl(jsonKey)
    # 检查是否已爬取并解析
    have = qdailyDB.checkJson(jsonType, jsonKey, jsonUrl)
    if (have == 0): 
        # 首先从本地获取
        jsonDict = readParseJson(jsonKey)
        if (not jsonDict):
            # 从网上爬取并解析Json
            jsonDict = qdailySpider.jsonParse(jsonUrl)
            writeParseJson(jsonKey, jsonDict)
            # 存储Json中无法解析的网站
            unknown = jsonDict['unknown']
            if (unknown):
                logfile = str(jsonKey)+'-json.log'
                unknownJsonSiteLog(unknown, logfile)
        # 获取解析文章网站，并存储
        artList = jsonDict['articles']
        while artList:
            art = artList.pop()
            have = qdailyDB.checkUrl(art['id'], art['type'], art['title'], art['url'])
            if (have == 0):
                store = qdailySpider.storeArticle(art['url'], art['id'])
                qdailyDB.markDoneUrl(art['url'])
            else:
                print("文章已存储")
        # 标记此Json文件
        qdailyDB.markDoneJson(jsonUrl)
    elif (have == 1):
        # 直接从本地获取
        jsonDict = readParseJson(jsonKey)
        if (not jsonDict):
            print('无本地文件\njsonKey: %s\nURL: %s' %(jsonKey, jsonUrl))
            raise Exception('错误：已记录的Json文件未保存！')
    jsonKey = jsonDict['lastKey']

if (not jsonKey):
    print("无Json文件待解析，爬取完毕！")



