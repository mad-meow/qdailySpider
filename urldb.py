# -*- coding: utf-8 -*-
import sqlite3
import os
import hashlib

# 存储url的数据库管理类
class Urldb:
    __dbdir = './urldb'
    __db = './urldb/qdailyURLs.db'
    # 对url计算MD5
    def getmd5(self, orgStr):
        utfStr = orgStr.encode('utf-8')
        md5val = hashlib.md5(utfStr).hexdigest()
        return md5val
    # 表结构：
    # 表1：文章记录表
    # num, type, id, title, url, have, md5
    # 表2：json记录表
    # num, type, key, url, have, md5
    # 初始化创建数据表
    def __init__(self):
        if (not os.path.isdir(self.__dbdir)):
            os.mkdir(self.__dbdir)
        self.__conn = sqlite3.connect(self.__db)
        self.__conn.row_factory = sqlite3.Row
        self.__cur = self.__conn.cursor()
        # 表1：文章url表
        try:
            createSql = '''CREATE TABLE articles (
            num INTEGER PRIMARY KEY AUTOINCREMENT,
            type TINYINT NOT NULL,
            id INTEGER NOT NULL,
            title TEXT NOT NULL,
            url TEXT DEFAULT unknown,
            have TINYINT DEFAULT 0,
            md5 TEXT NOT NULL UNIQUE
            );'''
            self.__cur.execute(createSql)
            self.__conn.commit()
            print("数据表 articles 创建成功！")
        except :
            print("数据表 articles 已创建！")
            pass
        # 表2：json文件数据表
        try:
            createSql = '''CREATE TABLE json (
            num INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            key INTEGER NOT NULL,
            url TEXT NOT NULL,
            have TINYINT DEFAULT 0,
            md5 TEXT NOT NULL UNIQUE
            );'''
            self.__cur.execute(createSql)
            self.__conn.commit()
            print("数据表 json 创建成功！")
        except:
            print("数据表 json 已创建！")
            pass
    
    # 添加文章url
    def addUrl(self, artid, arttype, arttitle, arturl):
        md5val = self.getmd5(arturl)
        insertSql = '''INSERT INTO articles (id, type, title, url, md5) 
            VALUES ("%s","%s","%s","%s", "%s");''' %(artid, arttype, arttitle, arturl, md5val)
        try:
            self.__cur.execute(insertSql)
            self.__conn.commit()
            print("成功添加文章\nURL: '%s' " %(arturl))
            return 0
        except Exception as err:
            print("文章添加失败！")
            print(err)
            return 1
            # selectSql = '''SELECT * FROM articles where md5 = "%s";''' %(md5val)
            # self.__cur.execute(selectSql)
            # re = self.__cur.fetchone()
            # if (not arturl == re['url']):
            #     print(err)
            #     print("------------")
            #     print("插入URL：%s\n插入MD5：%s" %(arturl, md5val))
            #     print("数据库URL：%s\n数据库MD5：%s" %(re['url'], re['md5']))
            #     raise Exception("同一MD5对应了不同URL！")
            # else:
            #     print(err)
            #     pass
    # 标记完成文章url
    def markDoneUrl(self, arturl):
        md5val = self.getmd5(arturl)
        updateSql = '''UPDATE articles SET have = 1 WHERE md5 = "%s";''' %(md5val)
        try:
            self.__cur.execute(updateSql)
            self.__conn.commit()
            print("爬取文章标记完成\nURL: '%s'" %(arturl))
            return 0
        except Exception as err:
            raise err
    # 获取所有未标记文章url
    def getUndoUrl(self):
        selectSql = "SELECT * FROM articles WHERE have = 0 ORDER BY num"
        self.__cur.execute(selectSql)
        queryRe = self.__cur.fetchall()
        re = []
        for index, member in enumerate(queryRe):
            if (member['url'] == 'unknown'):
                print('文章ID: %s URL未知' %(str(member['id'])))
            else:
                re.append('url')
        return re
    # 检查文章记录
    def checkUrl(self, artid, arttype, arttitle, arturl):
        md5val = self.getmd5(arturl)
        selectSql = "SELECT have FROM articles WHERE md5 = '%s';" %(md5val)
        self.__cur.execute(selectSql)
        re = self.__cur.fetchone()
        if (re):
            if (re['have'] > 0):
                print("文章记录已标记")
            else:
                print("文章记录未标记")
            return re['have']
        else:
            print("数据库中不存在该文章记录，将自动添加！")
            re = self.addUrl(artid, arttype, arttitle, arturl)
            if (re > 0):
                raise Exception('不存在的记录添加失败')
            else:
                return 0
    
    # 添加已获取的json文件id
    def addJson(self, jstype, jskey, jsurl):
        md5val = self.getmd5(jsurl)
        insertSql = '''INSERT INTO json (type, key, url, md5) 
            VALUES ("%s","%s","%s", "%s");''' %(jstype, jskey, jsurl, md5val)
        # print(insertSql)
        try:
            self.__cur.execute(insertSql)
            self.__conn.commit()
            print("成功添加Json文件\nID: %s\nURL: %s " %(jskey, jsurl))
            return 0
        except Exception as err:
            print("json文件添加失败")
            print(err)
            return 1
            # selectSql = '''SELECT * FROM json where key = "%s";''' %(jskey)
            # self.__cur.execute(selectSql)
            # re = self.__cur.fetchone()
            # if (not str(jskey) == str(re['key'])):
            #     print(err)
            #     print("------------")
            #     print("插入json id：%s" %(jsonid))
            #     raise Exception("Json文件ID添加失败")
    # 标记完成json
    def markDoneJson(self, jsurl):
        md5val = self.getmd5(jsurl)
        updateSql = '''UPDATE json SET have = 1 WHERE md5 ="%s";''' %(md5val)
        try:
            self.__cur.execute(updateSql)
            self.__conn.commit()
            print("Json文件标记完成\nURL %s" %(jsurl))
            return 0
        except Exception as err:
            raise err
    # 获取所有未标记json url
    def getUndoJson(self):
        selectSql = "SELECT * FROM json WHERE have = 0 ORDER BY num"
        self.__cur.execute(selectSql)
        queryRe = self.__cur.fetchall()
        re = []
        for index, member in enumerate(queryRe):
            re.append(member['url']) 
        return re
    # 检查json记录
    def checkJson(self, jstype, jskey, jsurl):
        md5val = self.getmd5(jsurl)
        selectSql = "SELECT have FROM json WHERE md5 = '%s';" %(md5val)
        self.__cur.execute(selectSql)
        re = self.__cur.fetchone()
        if (re):
            if (re['have'] > 0):
                print("Json文件已标记")
            else:
                print("Json文件未标记")
            return re['have']
        else:
            print("数据库中不存在该Json文件，将自动添加！")
            re = self.addJson(jstype, jskey, jsurl)
            if (re > 0):
                raise Exception("不存在的记录添加失败")
            else:
                return 0

    # 数据库通用语句
    def sqlExe(self, sql):
        self.__cur.execute(sql)
        self.__conn.commit()
        return self.__cur.fetchall()

    def test(self):
        print('test function')
