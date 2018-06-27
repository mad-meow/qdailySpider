# -*- coding: utf-8 -*-
import urllib.request
from bs4 import BeautifulSoup
import os
import json
import re

# 网页爬虫基类
class WebSpider:
    def __init__(self, opener = None):
        if (not isinstance(opener, urllib.request.OpenerDirector)):
            if (opener):
                print("初始化参数错误：opener参数类型不正确，将使用预设opener")
            httphd = urllib.request.HTTPHandler()
            httpshd = urllib.request.HTTPSHandler() # debuglevel = 1
            opener = urllib.request.build_opener(httphd, httpshd)
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
            opener.addheaders = headers
        self.opener = opener

    def getHtmlSoup(self, artUrl):
        try:
            webpage = self.opener.open(artUrl, timeout=10)
            html_soup = BeautifulSoup(webpage.read(), "lxml")
            return html_soup
        except Exception as e:
            print('错误：获取页面soup对象失败！')
            print(e)
            return 1

    def getRaw(self, url):
        try:
            source = self.opener.open(url, timeout = 10)
            return source.read()
        except Exception as e:
            print('错误：获取页面失败！')
            print(e)
            return 1

class ArticleWeb(WebSpider):
    __artdir = "./collections"
    __htmldir = __artdir + "/html"
    __textdir = __artdir + "/text"

    def __init__(self, opener = None):
        WebSpider.__init__(self, opener)
        if (not os.path.isdir(self.__artdir)):
            os.mkdir(self.__artdir)
        if (not os.path.isdir(self.__htmldir)):
            os.mkdir(self.__htmldir)
        if (not os.path.isdir(self.__textdir)):
            os.mkdir(self.__textdir)
    
    # 文章标题敏感字符处理
    def titleValid(self, inStr):
        pa = re.compile(r'[\\/:\*\?"<>\|]')
        outStr = pa.sub(' ', inStr)
        return outStr
    
    # 存储文章文本
    def storeText(self, html_soup, artid):
        artid = str(artid)
        title = html_soup.title.string
        title = str(artid) + '-'+ self.titleValid(title)
        content = html_soup.body.find('div', class_ = 'page-content')
        content_utf = str(content).encode('utf-8')
        outfile = self.__textdir + '/' + title + '.html'
        try:
            with open(outfile, 'wb') as f:
                f.write(content_utf)
            if (os.path.isfile(outfile)):
                print("文章文本存储成功: \n"+title)
                return 0
            else:
                print('文章文本存储失败！')
                return 1
        except Exception as e:
            print('文章文本存储失败！')
            print(e)
            return 1
    
    # 存储文章Web页面
    def storeWeb(self, html_soup, artid):
        # 每篇文章一个目录存储
        artid = str(artid)
        title = html_soup.title.string
        title = artid + '-'+ self.titleValid(title)
        outdir = self.__htmldir + '/' + title
        figdir = outdir + '/fig'
        outhtml = outdir + '/' + title + '.html'
        try:
            os.mkdir(outdir)
        except Exception as e:
            print(e)

        try:
            os.mkdir(figdir)
        except Exception as e:
            print(e)

        # 页面head部分的href添加域名
        webHead = html_soup.head
        def addLinkHref(tag):
            pa = re.compile(r'^http')
            if (tag.has_attr('href')):
                href = tag['href']
                if (not pa.match(href)):
                    tag['href'] = 'http://www.qdaily.com' + href
        webHead.find_all(addLinkHref)
        # 页面head部分src添加域名
        def addScriptSrc(tag):
            pa = re.compile(r'$http')
            if (tag.name == 'script'):
                if (tag.has_attr('src')):
                    src = tag['src']
                    if (not pa.match(src)):
                        tag['src'] = 'http://www.qdaily.com' + src
        html_soup.body.find_all(addScriptSrc)
        # 下载图片并补全src
        figRe = re.compile(r'^http.*/')
        figures = html_soup.body.find('div', class_ = 'detail').find_all('figure')
        for ele in figures:
            img = ele.find('img')
            try:
                figUrl = img['data-src']
                figFile = figRe.sub(figdir + '/', figUrl)
                figData = self.getRaw(figUrl)
                if (not figData == 1):
                    with open(figFile, 'wb') as f:
                        f.write(figData)
                    img['data-src'] = figRe.sub('./fig/', img['data-src'])
            except Exception as e:
                print(e)
                print("图片存储失败：\n")
            
        content = html_soup.html
        content_utf = str(content).encode('utf-8')

        try:
            with open(outhtml, 'wb') as f:
                f.write(content_utf)
            if (os.path.isfile(outhtml)):
                print("文章页面存储成功：\n" + title + "\n存储目录：\n" + outdir)
                # return {'figdir': figdir, 'figUrlList': figUrlList}
                return 0
            else:
                print('错误：文章页面存储失败！')
                return 1
        except Exception as e:
            print('错误：文章页面存储失败！')
            print(e)
            return 1

    # 存储文章，调用此函数完成存储动作
    def storeArticle(self, articleUrl, artid):
        html_soup = self.getHtmlSoup(articleUrl)
        artText = self.storeText(html_soup, artid)
        artWeb = self.storeWeb(html_soup, artid)
        if (artText == 0 and artWeb == 0):
            return 0
        else:
            return 1

class QDailyWeb(ArticleWeb):
    entryUrl = None
    artType = {'articles': 2, 'cards': 12}
    def __init__(self, entryUrl, opener = None):
        ArticleWeb.__init__(self, opener)
        self.entryUrl = entryUrl
    
    # 入口页面分析
    def entryWeb(self):
        html_soup = self.getHtmlSoup(self.entryUrl)
        artContainer = html_soup.body.find('div', class_ = 'packery-container articles')
        lastKey = artContainer['data-lastkey']
        artDivs = artContainer.find_all('div', class_ = 'packery-item')
        artList = []
        pa = re.compile(r'\/(.*)\/(\d+)\.html')
        for ele in artDivs:
            a = ele.find('a')
            href = a['href']
            arttitle = self.titleValid(a.find('h3', class_ = 'title').string)
            ma = pa.match(href)
            if (ma):
                artid = ma.group(2)
                arttype = self.artType[ma.group(1)]
            else:
                raise Exception('链接: %s 捕获失败' %(href))
            artList.append({'id': artid, 'type': arttype, 'title': arttitle, 'url': 'http://www.qdaily.com' + href})
        return {'lastKey': lastKey, 'artList': artList}

    # Json对象获取并解析
    def jsonParse(self, jsonUrl):
        jsonSource = self.getRaw(jsonUrl)
        jsonStr = jsonSource.decode('utf-8')
        jsonObj = json.loads(jsonStr)
        lastKey = jsonObj['data']['last_key']
        articles = []
        unknown = []
        for art in jsonObj['data']['feeds']:
            artType = art['type']
            artID = art['post']['id']
            artTitle = self.titleValid(art['post']['title'])
            if (artType == 2):
                artUlr = 'http://www.qdaily.com/articles/' + str(artID) + '.html'
            elif (artType == 12):
                artUlr = 'http://www.qdaily.com/cards/' + str(artID) + '.html'
            else:
                print("未知文章分类："+str(artType))
                artUrl = None

            addArt = {'type': artType, 'id': artID, 'title': artTitle, 'url': artUlr}

            if (addArt['url']):
                articles.append(addArt)
            else:
                unknown.append(unknown)
        return {'lastKey': lastKey, 'articles': articles, 'unknown': unknown}

    def testentry(self):
        html_soup = self.getHtmlSoup(self.entryUrl)
        print('----------------------')
        artContainer = html_soup.body.find('div', class_ = 'packery-container articles')
        return artContainer


