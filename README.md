# 裁判文书网爬虫（2018-09-17）
> 目标：两万一审刑事判决书文书，以案例ID为文件名称。
## 文件说明 ##
 - checkCode.jpg 验证码jpg文件。
 - content.html 请求文书html模板。
 - dateFile.txt 从2016-01-01到2018-09-01日期列表。
 - processFile.txt 已经处理过的日期列表。
 - docid.js 文书ID解密JS文件。
 - getKey3.js 加解密工具文件。
 - vl5x.js 加密获取参数vl5x。
 - wenshu.db 存放文书ID等信息的sqlite3数据库。
 - download 存放文书下载的doc文件目录。
 - test.py 测试文件。
 - court_thread.py 从法律判决书网获取文书ID，存放至sqlite3数据库。
 - downloadfile.py 从sqlite3数据库中获取文书ID，下载。
 - requirements.txt 本程序依赖的Python第三方包。
<br/><br/><br/>

## 运行说明 ##
- 1.运行court_thread.py，当出现 "出现验证码>>>>>" 时，打开checkCode.jpg输入图像验证码，
  输入完毕后请及时关闭jpg文件；当出现"完蛋了，被墙了!"，当前IP可能已经被网站列入反爬名单。
  该接口做了访问次数限制，除非跟换IP或使用代理，目前没有比较好的解决方案。限制在每天中午12点
  会取消重置。
  
- 2.运行downloadfile.py，当出现"出现验证码!"，"出现验证码>>>>>"打开checkCode.jpg输入
  图像验证码，输入完毕后请及时关闭jpg文件；再次运行downloadfile.py继续下载。目前下载文书
  接口只做了多次调用后图形验证码验证，没有做访问
  次数限制。
