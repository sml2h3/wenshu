# -*-encoding:utf-8-*-
"""
author: ex-zhuge001
date: 2018-09-17
desc: 从裁判文书网获取文书ID存放至sqlite3数据库
reference：https://github.com/sixs/wenshu_spider
"""
import requests
from urllib import parse
import execjs
import json
import re
import random
from bs4 import BeautifulSoup
import sqlite3
from time import sleep


# 爬虫代理
def get_proxy():
    r = requests.get('http://39.107.127.240:9000/get/')
    proxies = BeautifulSoup(r.text, "lxml").get_text()
    proxies = {"http": "http://{}".format(proxies.strip())}
    return proxies


session = requests.Session()
with open('./getKey3.js') as fp:
    js = fp.read()
    ctx = execjs.compile(js)

with open('./docid.js') as fp:
    js = fp.read()
    ctx2 = execjs.compile(js)


def get_guid():
    """
    获取guid参数
    """

    # # 原始js版本
    # js1 = '''
    #   function getGuid() {
    #         var guid = createGuid() + createGuid() + "-" + createGuid() + "-" + createGuid() + createGuid() + "-" + createGuid() + createGuid() + createGuid(); //CreateGuid();
    #           return guid;
    #     }
    #     var createGuid = function () {
    #         return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
    #     }
    # '''
    # ctx1 = execjs.compile(js1)
    # guid = (ctx1.call("getGuid"))
    # return guid

    # 翻译成python
    def createGuid():
        return str(hex((int(((1 + random.random()) * 0x10000)) | 0)))[3:]

    return '{}{}-{}-{}{}-{}{}{}' \
        .format(
        createGuid(), createGuid(),
        createGuid(), createGuid(),
        createGuid(), createGuid(),
        createGuid(), createGuid()
    )


def get_number(guid):
    """
    获取number
    """
    codeUrl = "http://wenshu.court.gov.cn/ValiCode/GetCode"
    data = {
        'guid': guid
    }
    headers = {
        'Host': 'wenshu.court.gov.cn',
        'Origin': 'http://wenshu.court.gov.cn',
        'Referer': 'http://wenshu.court.gov.cn/',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
    }
    req1 = session.post(codeUrl, data=data, headers=headers)
    number = req1.text
    return number


def get_vjkl5(guid, number, Param):
    """
    获取cookie中的vjkl5
    """
    url1 = "http://wenshu.court.gov.cn/list/list/?sorttype=1&number=" + number + "&guid=" + guid + "&conditions=searchWord+QWJS+++" + parse.quote(
        Param)
    Referer1 = url1
    headers1 = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Host": "wenshu.court.gov.cn",
        "Proxy-Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"
    }
    req1 = session.get(url=url1, headers=headers1, timeout=10)
    try:
        vjkl5 = req1.cookies["vjkl5"]
        return vjkl5
    except:
        return get_vjkl5(guid, number, Param)


def get_vl5x(vjkl5):
    """
    根据vjkl5获取参数vl5x
    """
    vl5x = (ctx.call('getKey3', vjkl5))
    return vl5x


def check_code(checkcode='', isFirst=True):  # 是否传入验证码,是否第一次验证码错误
    """
    验证码识别，参数为checkcode和isFirst，用于标识是否为第一次验证码识别，
    第一次识别需要下载验证码，由于文书验证码验证经常出现验证码正确但
    但会验证码错误情况，所以第一次验证码错误时不会下载新的验证码.
    """
    if checkcode == '':
        check_code_url = 'http://wenshu.court.gov.cn/User/ValidateCode'
        headers = {
            'Host': 'wenshu.court.gov.cn',
            'Origin': 'http://wenshu.court.gov.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
        }
        req = session.get(check_code_url, headers=headers)
        fp = open('./checkCode.jpg', 'wb')
        fp.write(req.content)
        fp.close()
        checkcode = input()
        #checkcode = distinguish('checkCode.jpg')
    print('识别验证码为：{0}'.format(checkcode))
    check_url = 'http://wenshu.court.gov.cn/Content/CheckVisitCode'
    headers = {
        'Host': 'wenshu.court.gov.cn',
        'Origin': 'http://wenshu.court.gov.cn',
        'Referer': 'http://wenshu.court.gov.cn/Html_Pages/VisitRemind.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    }
    data = {
        'ValidateCode': checkcode
    }
    req = session.post(check_url, data=data, headers=headers)
    if req.text == '2':
        print('验证码错误')
        if isFirst:
            check_code(checkcode, False)
        else:
            check_code()


def get_tree_content(Param):
    """
    获取左侧类目分类
    """
    guid = get_guid()
    number = get_number(guid)
    vjkl5 = get_vjkl5(guid, number, Param)
    vl5x = get_vl5x(vjkl5)
    url = 'http://wenshu.court.gov.cn/List/TreeContent'
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "wenshu.court.gov.cn",
        "Origin": "http://wenshu.court.gov.cn",
        "Proxy-Connection": "keep-alive",
        "Referer": "http://wenshu.court.gov.cn/list/list/?sorttype=1&number={0}&guid={1}&conditions=searchWord+QWJS+++{2}".format(
            number, guid, parse.quote(Param)),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    data = {
        "Param": Param,
        "vl5x": vl5x,
        "number": number,
        "guid": guid
    }
    req = session.post(url, headers=headers, data=data)
    json_data = json.loads(req.text.replace('\\', '').replace('"[', '[').replace(']"', ']'))
    tree_dict = {}
    for type_data in json_data:
        type_name = type_data['Key']
        type_dict = {
            'IntValue': type_data['IntValue'],
            'ParamList': []
        }
        for data in type_data['Child']:
            if data['IntValue']:
                type_dict['ParamList'].append({'Key': data['Key'], 'IntValue': data['IntValue']})
        tree_dict[type_name] = type_dict
    return tree_dict


def decrypt_id(RunEval, id):
    """
    docid解密
    """
    js = ctx2.call("GetJs", RunEval)
    js_objs = js.split(";;")
    js1 = js_objs[0] + ';'
    js2 = re.findall(r"_\[_\]\[_\]\((.*?)\)\(\);", js_objs[1])[0]
    key = ctx2.call("EvalKey", js1, js2)
    key = re.findall(r"\"([0-9a-z]{32})\"", key)[0]
    docid = ctx2.call("DecryptDocID", key, id)
    return docid


def get_data(Param, Page, Order, Direction, start_date):
    """
    获取数据
    """

    Index = 1  # 第几页

    guid = get_guid()
    number = get_number(guid)
    vjkl5 = get_vjkl5(guid, number, Param)
    vl5x = get_vl5x(vjkl5)

    while (True):

        print('###### 第{0}页 ######'.format(Index))

        # 获取数据
        url = "http://wenshu.court.gov.cn/List/ListContent"
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "wenshu.court.gov.cn",
            "Origin": "http://wenshu.court.gov.cn",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://wenshu.court.gov.cn/list/list/?sorttype=1&number={0}&guid={1}&conditions=searchWord+QWJS+++{2}".format(
                number, guid, parse.quote(Param)),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        data = {
            "Param": Param,
            "Index": Index,
            "Page": Page,
            "Order": Order,
            "Direction": Direction,
            "vl5x": vl5x,
            "number": number,
            "guid": guid
        }

        req = session.post(url, headers=headers, data=data)

        req.encoding = 'utf-8'
        return_data = req.text.replace('\\', '').replace('"[', '[').replace(']"', ']') \
            .replace('＆ｌｄｑｕｏ;', '“').replace('＆ｒｄｑｕｏ;', '”')

        if return_data == '"remind"' or return_data == '"remind key"':

            print('出现验证码'+'>'*5)

            check_code()

            guid = get_guid()
            number = get_number(guid)

        else:
            #print(return_data)
            if '<span>360安域</span>' in return_data:
                print('!'*20+'完蛋了，被墙了'+'!'*20)
            json_data = json.loads(return_data)
            if not len(json_data):
                print('采集完成')
                break
            else:
                RunEval = json_data[0]['RunEval']
                for i in range(1, len(json_data)):
                    name = json_data[i]['案件名称'] if '案件名称' in json_data[i] else ''
                    court = json_data[i]['法院名称'] if '法院名称' in json_data[i] else ''
                    number = json_data[i]['案号'] if '案号' in json_data[i] else ''
                    type = json_data[i]['案件类型'] if '案件类型' in json_data[i] else ''
                    id = json_data[i]['文书ID'] if '文书ID' in json_data[i] else ''
                    id = decrypt_id(RunEval, id)
                    date = json_data[i]['裁判日期'] if '裁判日期' in json_data[i] else ''
                    data_dict = dict(
                        id=id,
                        name=name,
                        type=type,
                        date=date,
                        number=number,
                        court=court
                    )
                    print(data_dict)
                    save_sqlite(data_dict)
                    #bb = data_dict['number']
                    #download(bb)

            Index += 1

            guid = get_guid()
            number = get_number(guid)

        if Index == 10:
            save_data('./processFile.txt', start_date)
            break


def save_data(filename,data):
    """
    数据存储逻辑
    """
    print(filename,data)
    a = open(filename,'a')
    a.write(data+'\n')
    a.close()

def save_sqlite(data_dict):
    """
    {'id': 'b2a9c613-8dca-41ac-b584-873541901a4d', 'name': '被告人蓝同辉犯盗窃罪一案一审刑事判决书', 'type': '1', 'date': '2015-01-12', 'number': '（2015）西刑初字第88号', 'court': '广西壮族自治区高级人民法院'}
    """
    conn = sqlite3.connect('./wenshu.db')
    cur = conn.cursor()
    id = data_dict['id']
    name = data_dict['name']
    type = data_dict['type']
    date_time = data_dict['date']
    number = data_dict['number']
    court = data_dict['court']

    sql = '''insert into wenshu (id, name, type, date_time, number, court) 
          values (:st_id,:st_name,:st_type,:st_date_time,:st_number,:st_court)'''
    try:
        cur.execute(sql,{'st_id':id,'st_name':name,'st_type':type,'st_date_time':date_time,'st_number':number,'st_court':court})
    except Exception as e:
        print(e)
    conn.commit()
    cur.close()
    conn.close()

def getCourtInfo(DocID):
    """
    根据文书DocID获取相关信息：标题、时间、浏览次数、内容等详细信息
    """
    url = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={0}'.format(DocID)
    headers = {
        'Host': 'wenshu.court.gov.cn',
        'Origin': 'http://wenshu.court.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    }
    req = session.get(url, headers=headers)
    print(req.text)
    req.encoding = 'uttf-8'
    return_data = req.text.replace('\\', '')
    read_count = re.findall(r'"浏览\：(\d*)次"', return_data)[0]
    court_title = re.findall(r'\"Title\"\:\"(.*?)\"', return_data)[0]
    court_date = re.findall(r'\"PubDate\"\:\"(.*?)\"', return_data)[0]
    court_content = re.findall(r'\"Html\"\:\"(.*?)\"', return_data)[0]
    return [court_title, court_date, read_count, court_content]


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
    print('"{}"文件下载完成...'.format(filename))


if __name__ == '__main__':

    #### 构造检索条件 ####
    # 检索关键词
    keyword = '*'
    # 检索类型
    search_type_list = ['全文检索', '首部', '事实', '理由', '判决结果', '尾部']
    search_type = search_type_list[0]
    # 案由
    # case_list = ['全部', '刑事案由', '民事案由', '行政案由', '赔偿案由']
    case_list = ['全部']
    case = case_list[0]
    # 法院层级
    court_type_list = ['全部', '最高法院', '高级法院', '中级法院', '基层法院']
    court_type = court_type_list[0]
    # 案件类型
    # case_type_list = ['全部', '刑事案件', '民事案件', '行政案件', '赔偿案件','执行案件']
    case_type_list = ['刑事案件']
    case_type = case_type_list[0]
    # 审判程序
    # case_process_list = ['全部', '一审', '二审', '再审', '复核', '刑罚变重', '再审审查与审判监督','其他']
    case_process_list = ['一审']
    case_process = case_process_list[0]
    # 文书类型
    wenshu_type_list = ['全部', '裁判书', '调解书', '决定书', '通知书', '批复', '答复', '函', '令', '其他']
    wenshu_type = wenshu_type_list[0]
    # 裁判日期
    # TODO
    handlelist = []
    with open('./dateFile.txt', 'r') as fin:
        fileorg = [line.strip() for line in fin]
    with open('./processFile.txt', 'r') as fin:
        filehandle = [line.strip() for line in fin]
    handlelist = list(set(fileorg) - set(filehandle))
    print(handlelist)

    for i in handlelist:
        print(i)
        start_date = i
        end_date = i

        # 法院地域，需要二次获取，判断那些省份的法院有数据
        court_loc_list = ['全部']
        court_loc = court_loc_list[0]
        param_list = []
        param_list.append("{0}:{1}".format(search_type, keyword))
        if case != '全部':
            param_list.append("案由:{}".format(case))
        if court_type != '全部':
            param_list.append("法院层级:{}".format(court_type))
        if case_type != '全部':
            param_list.append("案件类型:{}".format(case_type))
        if case_process != '全部':
            param_list.append("审判程序:{}".format(case_process))
        if wenshu_type != '全部':
            param_list.append("文书类型:{}".format(wenshu_type))
        param_list.append("裁判日期:{0} TO {1}".format(start_date, end_date))
        if court_loc != '全部':
            param_list.append("法院地域:{}".format(court_loc))
        Param = ','.join(param_list)
        # Param = "全文检索:*"
        Page = 20  # 每页几条
        Order = "法院层级"  # 排序标准
        Direction = "asc"  # asc正序 desc倒序
        print(Param)
        get_data(Param, Page, Order, Direction,start_date)
        sleep(3)
