#coding:utf-8
import urllib
import urllib.request
import multiprocessing
from bs4 import BeautifulSoup
import re
import os
import time

def get_pages(url):
    soup=""
    try:
        # 创建请求日志文件夹
        if 'Log' not in os.listdir('.'):
            os.mkdir(r".\Log")

        # 请求当前章节页面  params为请求参数
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        content = response.read()
        data = content.decode('gbk')
        # soup转换
        soup = BeautifulSoup(data, "html.parser")

    except Exception as e:
        print(url+" 请求错误\n")
        with open(r".\Log\req_error.txt",'a',encoding='utf-8') as f:
            f.write(url+" 请求错误\n")
        f.close()
    return soup

# 通过章节的url下载内容，并返回下一页的url
def get_ChartTxt(url,title,num):
    soup=get_pages(url)

    # 获取章节名称
    subtitle = soup.select('#htmltimu')[0].text
    # 判断是否有感言
    if re.search(r'.*?章', subtitle) is  None:
        return
    # 获取章节文本
    content = soup.select('#htmlContent')[0].text
    # 按照指定格式替换章节内容，运用正则表达式
    content = re.sub(r'\(.*?\)', '', content)
    content = re.sub(r'\r\n', '', content)
    content = re.sub(r'\n+', '\n', content)
    content = re.sub(r'<.*?>+', '', content)


    # 单独写入这一章
    try:
        with open(r'.\%s\%s %s.txt' % (title, num,subtitle), 'w', encoding='utf-8') as f:
            f.write(subtitle + content)
        f.close()
        print(num,subtitle, '下载成功')

    except Exception as e:
        print(subtitle, '下载失败',url)
        errorPath='.\Error\%s'%(title)
        # 创建错误文件夹
        try :
            os.makedirs(errorPath)
        except Exception as e:
            pass
        #写入错误文件
        with open("%s\error_url.txt"%(errorPath),'a',encoding='utf-8') as f:
            f.write(subtitle+"下载失败 "+url+'\n')
        f.close()
    return


# 通过首页获得该小说的所有章节链接后下载这本书
def thread_getOneBook(indexUrl):
    soup = get_pages(indexUrl)
    # 获取书名
    title = soup.select('#htmldhshuming')[0].text
    # 根据书名创建文件夹
    if title not in os.listdir('.'):
        os.mkdir(r".\%s" % (title))
        print(title, "文件夹创建成功———————————————————")

    # 加载此进程开始的时间
    print('下载 %s 的PID：%s...' % (title, os.getpid()))
    start = time.time()

    # 获取这本书的所有章节
    charts_url = []
    # 提取出书的每章节不变的url
    indexUrl = re.sub(r'index.html', '', indexUrl)
    charts = soup.select(".zjlist4 li a")
    for i in charts:
        # print(j+i.attrs['href'])
        charts_url.append(indexUrl + i.attrs['href'])

    # 创建下载这本书的进程
    p = multiprocessing.Pool()
    #自己在下载的文件前加上编号，防止有的文章有上，中，下三卷导致有3个第一章
    num=1
    for i in charts_url:
        p.apply_async(get_ChartTxt, args=(i,title,num))
        num+=1
    print('等待 %s 所有的章节被加载......' % (title))
    p.close()
    p.join()
    end = time.time()
    print('下载 %s  完成，运行时间  %0.2f s.' % (title, (end - start)))
    print('开始生成 %s ................' %title )
    sort_allCharts(r'.',"%s.txt"%title)
    return

# 创建下载多本书书的进程
def process_getAllBook(base):
    # 输入你要下载的书的首页地址
    print('主程序的PID：%s' % os.getpid())
    book_indexUrl=[
        'http://www.yznnw.com/files/article/html/1/1129/index.html',
        'http://www.yznnw.com/files/article/html/29/29931/index.html',
        'http://www.yznnw.com/files/article/html/0/868/index.html'
    ]
    print("-------------------开始下载-------------------")
    p = []
    for i in book_indexUrl:
        p.append(multiprocessing.Process(target=thread_getOneBook, args=(i,)))
    print("等待所有的主进程加载完成........")
    for i in p:
        i.start()
    for i in p:
        i.join()
    print("-------------------全部下载完成-------------------")

    return

#合成一本书
def sort_allCharts(path,filename):
    lists=os.listdir(path)
    # 对文件排序
    # lists=sorted(lists,key=lambda i:int(re.match(r'(\d+)',i).group()))
    lists.sort(key=lambda i:int(re.match(r'(\d+)',i).group()))
    # 删除旧的书
    if os.path.exists(filename):
        os.remove(filename)
        print('旧的 %s 已经被删除'%filename)
    # 创建新书
    with open(r'.\%s'%(filename),'a',encoding='utf-8') as f:
        for i in lists:
            with open(r'%s\%s' % (path, i), 'r', encoding='utf-8') as temp:
                f.writelines(temp.readlines())
            temp.close()
    f.close()
    print('新的 %s 已经被创建在当前目录 %s '%(filename,os.path.abspath(filename)))

    return


if __name__=="__main__":
    # # 主页
    base = 'http://www.yznnw.com'
    # 下载指定的书
    process_getAllBook(base)
    # sort_allCharts(r'.\龙血战神',"龙血战神.txt")
    # sort_allCharts(r'.\武道天下',"武道天下.txt")
    # sort_allCharts(r'.\修罗武神',"修罗武神.txt")