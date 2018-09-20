'''
import requests
from bs4 import BeautifulSoup
import lxml

def get_proxy():
    r = requests.get('http://39.107.127.240:9000/get/')
    proxies = BeautifulSoup(r.text, "lxml").get_text()
    proxies = {"http": "http://{}".format(proxies.strip())}
    print(proxies)
    return proxies

def delete_proxy(proxy):
    requests.get('http://39.107.127.240:9000/delete/?proxy={}'.format(proxy))

aa = get_proxy()
delete_proxy(aa)

import datetime

start = '2015-12-31'
end = '2018-09-01'

datestart = datetime.datetime.strptime(start, '%Y-%m-%d')
dateend = datetime.datetime.strptime(end, '%Y-%m-%d')

while datestart < dateend:
    datestart += datetime.timedelta(days=1)
    aa = datestart.strftime('%Y-%m-%d')
    print(aa)


handlelist = []
with open('./dateFile.txt', 'r') as fin:
    fileorg = [line.strip() for line in fin]
with open('./processFile.txt', 'r') as fin:
    filehandle = [line.strip() for line in fin]
handlelist = list(set(fileorg)-set(filehandle))
print(handlelist)

import requests
def get_proxy():
    #r = requests.get('http://39.107.127.240:9000/get/')
    r = requests.get('http://218.94.57.203/t0918/get')
    #proxies = BeautifulSoup(r.text, "lxml").get_text()
    #proxies = {"http": "http://{}".format(proxies.strip())}
    proxies = {"http": "http://{}".format(r.text)}
    return proxies

def delete_proxy(proxy):
    """
    删除:
    curl -i "http://218.94.57.203/t0918/delete?proxy=127.0.0.2:8080"
    """
    #requests.get('http://39.107.127.240:9000/delete/?proxy={}'.format(proxy))
    for k in proxy:
        ip = proxy[k]
        requests.get("http://218.94.57.203/t0918/delete?proxy=" + ip.split(":")[1])

aa = get_proxy()
print(aa)
'''

import requests
from urllib import parse
session = requests.Session()

def download(DocID):
    """
    根据文书DocID下载doc文档
    """
    #courtInfo = getCourtInfo(DocID)
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
    print('"{}"文件下载完成...'.format(filename))

