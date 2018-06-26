# -*- coding: utf-8 -*-
import urllib.request
import os
from bs4 import BeautifulSoup

class WebSpider:
	def __init__(self, opener = None):
		if (not isinstance(opener, urllib.request.OpenerDirector)):
			if (opener):
				print("Error in opener class. The deafult opener will be used.")
			httphd = urllib.request.HTTPHandler(debuglevel = 1)
			httpshd = urllib.request.HTTPSHandler(debuglevel = 1)
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
			html_soup = BeautifulSoup(webpage.read())
			return html_soup
		except Exception as e:
			print('Error: failed to get webpage!')
			print(e)
			return 1

	def getRaw(self, url):
		try:
			source = self.opener.open(url, timeout = 10)
			return source.read()
		except Exception as e:
			print('Error: failed to get web source!')
			print(e)
			return 1

	# def getArticleFigs(self, figUrlList, figdir):
	# 	pa = re.compile(r'^http.*/')
	# 	for figUrl in figUrlList:
	# 		filePath = pa.sub(figdir + '/', figUrl)
	# 		try:
	# 			with open(filePath, 'wb') as f:
	# 				figSource = self.opener.open(figUrl, timeout = 10)
	# 				f.write(figSource.read())
	# 		except Exception as e:
	# 			raise e
	# 	return 0


class WebFactory:
	__artdir = "./collections"
	__htmldir = __artdir + "/html"
	__textdir = __artdir + "/text"

	def __init__(self):
		if (not os.path.isdir(self.__artdir)):
			os.mkdir(self.__artdir)
		if (not os.path.isdir(self.__htmldir)):
			os.mkdir(self.__htmldir)
		if (not os.path.isdir(self.__textdir)):
			os.mkdir(self.__textdir)

	def titleValid(self, inStr):
		pa = re.compile(r'[\\/:\*\?"<>\|]')
		outStr = pa.sub('', inStr)
		return outStr

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
				print("Save articl text: \n"+title)
				return 0
			else:
				print('Error: failed to store web text!')
				return 1
		except Exception as e:
			print('Error: failed to store web text!')
			print(e)
			return 1

	def storeWeb(self, opener, html_soup, artid):
		# each article a dir
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

		# add head to link.href
		webHead = html_soup.head
		def addLinkHref(tag):
			pa = re.compile(r'^http')
			if (tag.has_attr('href')):
				href = tag['href']
				if (not pa.match(href)):
					tag['href'] = 'http://www.qdaily.com' + href
		webHead.find_all(addLinkHref)
		# add head to scrtipt.src
		def addScriptSrc(tag):
			pa = re.compile(r'$http')
			if (tag.name == 'script'):
				if (tag.has_attr('src')):
					src = tag['src']
					if (not pa.match(src)):
						tag['src'] = 'http://www.qdaily.com' + src
		html_soup.body.find_all(addScriptSrc)
		# download figures and replace src in html
		figRe = re.compile(r'^http.*/')
		figures = html_soup.body.find('div', class_ = 'detail').find_all('figure')
		for ele in figures:
			img = ele.find('img')
			figUrl = img['data-src']
			figFile = figRe.sub(figdir + '/', figUrl)
			try:
				with open(figFile, 'wb') as f:
					f.write(opener.open(figUrl).read())
				img['data-src'] = figRe.sub('./fig/', img['data-src'])
			except Exception as e:
				print(e)
				print("Failed to save fig:\n" + figUrl)
			
		content = html_soup.html
		content_utf = str(content).encode('utf-8')

		try:
			with open(outhtml, 'wb') as f:
				f.write(content_utf)
			if (os.path.isfile(outhtml)):
				print("Save article html:\n" + title + "\ndir:\n" + outdir)
				# return {'figdir': figdir, 'figUrlList': figUrlList}
				return 0
			else:
				print('Error: failed to store web text!')
				return 1
		except Exception as e:
			print('Error: failed to store web text!')
			print(e)
			return 1



teurl = "http://www.qdaily.com/tags/1068.html"
artSpi = WebSpider()
html_soup = artSpi.getHtmlSoup(teurl)
with open('./home.html', 'wb') as f:
    content = html_soup.html
    content_utf = str(content).encode('utf-8')
    f.write(content_utf)
#artFac = WebFactory()
#artFac.storeText(html_soup, 54170)
#artFac.storeWeb(artSpi.opener, html_soup, 54170)
artSpi = WebSpider()
jsonUrl = 'http://www.qdaily.com/tags/tagmore/1068/1528236359.json'
jsonSource = artSpi.getRaw(jsonUrl)
jsonStr = jsonSource.decode('utf-8')
with open('jsontxt2.json', 'wb') as f:
    f.write(jsonSource)
import json
te = json.loads(jsonStr)

arts = te['data']['feeds']
count = 0
for i in te['data']['feeds']:
    print(i)
    count += 1
    if (count > 1):
        break
art = arts[0]

artType = art['type']

artID = art['post']['id']
