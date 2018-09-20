# -*-encoding:utf-8-*-
"""
author: ex-zhuge001
date: 2018-09-17
desc: 从sqlite3数据库，获取文书ID进行下载
reference：https://github.com/sixs/wenshu_spider
"""
import sqlite3
import requests
from urllib import parse
import re
from multiprocessing import Process
import time

session = requests.Session()

UA_list=[
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.86 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.87 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.88 Safari/537.36",

    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_7_8; en-us) AppleWebKit/534.51 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_7_8; en-us) AppleWebKit/534.52 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_7_8; en-us) AppleWebKit/534.53 (KHTML, like Gecko) Version/5.1 Safari/534.50",

]


def random_UA():
    import random
    return random.choice(UA_list)

def sleep(s=3):
    import time
    import random
    tts = round(0.1 + random.random() * s, 3)
    print("休息:{}s".format(tts))
    time.sleep(tts)

def _counter():
    iCount = 0
    def __counter():
        nonlocal iCount
        iCount = iCount +1
        return iCount
    return __counter

counter = _counter()

def getCourtInfo(DocID):
    """
    根据文书DocID获取相关信息：标题、时间、浏览次数、内容等详细信息
    """
    url = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={0}'.format(DocID)
    headers = {
        'Host': 'wenshu.court.gov.cn',
        'Origin': 'http://wenshu.court.gov.cn',
        'User-Agent': random_UA(),
    }
    cc = counter()

    req = session.get(url, headers=headers)
    if 'Remind' in req.text:
        print('!'*20+'出现验证码'+'!'*20)
    #print(req.text)
    req.encoding = 'utf-8'
    return_data = req.text.replace('\\', '')
    #print(return_data)
    try:
        read_count = re.findall(r'"浏览\：(\d*)次"', return_data)[0]
    except Exception as e:
        print("http status_code: ", req.status_code)
        print("http content:", return_data)
        print("完成数量: ", cc - 1)
        raise e

    court_title = re.findall(r'\"Title\"\:\"(.*?)\"', return_data)[0]
    court_date = re.findall(r'\"PubDate\"\:\"(.*?)\"', return_data)[0]
    court_content = re.findall(r'\"Html\"\:\"(.*?)\"', return_data)[0]
    return [court_title, court_date, read_count, court_content]

def updateDB(DocID):
    conn = sqlite3.connect('./wenshu.db')
    cur = conn.cursor()
    sql = "update main.wenshu set status = 1 where id = ?"
    cur.execute(sql,(DocID,))
    conn.commit()
    cur.close()
    conn.close()

def download(DocID):
    """
    根据文书DocID下载doc文档
    """
    courtInfo = getCourtInfo(DocID)
    url = 'http://wenshu.court.gov.cn/Content/GetHtml2Word'
    headers = {
        'Host': 'wenshu.court.gov.cn',
        'Origin': 'http://wenshu.court.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    }
    fp = open('content.html', 'r', encoding='utf-8')
    htmlStr = fp.read()
    fp.close()
    htmlStr = htmlStr.replace('court_title', courtInfo[0]).replace('court_date', courtInfo[1]). \
        replace('read_count', courtInfo[2]).replace('court_content', courtInfo[3])
    htmlName = courtInfo[0]
    data = {
        'htmlStr': parse.quote(htmlStr),
        'htmlName': parse.quote(htmlName),
        'DocID': DocID
    }
    req = session.post(url, headers=headers, data=data)
    filename = './download/{}.doc'.format(DocID)
    fp = open('{}'.format(filename), 'wb')
    fp.write(req.content)
    fp.close()
    updateDB(DocID)
    print('"{}"文件下载完成...'.format(filename))

def idlist():
    conn = sqlite3.connect('./wenshu.db')
    cur = conn.cursor()
    sql = "select id from main.wenshu where status = 0"
    cur.execute(sql)
    ids = cur.fetchall()
    list1 = []
    for i in ids:
        list1.append(i[0])
    #print(list1)
    cur.close()
    conn.close()
    return list1

if __name__ == '__main__':
    handlist = idlist()
    for i in handlist:
        p = Process(target=download,args=(i,))
        p.start()