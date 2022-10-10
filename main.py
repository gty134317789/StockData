import requests
import random
from bs4 import BeautifulSoup as bs
import time
import redis
import re
import json

#获取股票名称
def get_stock_names():
    #通过东方财富网上爬取股票的名称代码,存入本地txt文档
    url = "http://quote.eastmoney.com/stocklist.html"
    headers = {
        'Referer': 'http://quote.eastmoney.com/center/gridlist.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }

    # 网站编码为gbk 需要解码
    response = requests.get(url, headers=headers).content.decode('utf-8')
    soup = bs(response, 'lxml')
    all_ul = soup.find('div', id='table_wrapper-table').find_all('ul')  # 获取两个ul 标签数据
    with open('stock_names.txt', 'w+', encoding='utf-8') as f:
        for ul in all_ul:
            # 获取ul 下的所有的a 标签
            all_a = ul.find_all('a')
            for a in all_a:
                f.write(a.text + '\n')

#获取股票数据
def get_data(stocklist, outfile=r'E:\PycharmProjects\BigDataSight\stockdata'):
    headers = {
        'Referer': 'http://quotes.money.163.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    print(stocklist)
    # filelist = [os.path.splitext(file)[0] for file in os.listdir(r'E:\PycharmProjects\BigDataSight\stockdata')]
    for stock_code, stock_name in stocklist:
        # if stock_code in filelist: continue
        try:
            # stock_code = stock_name.split('(')[1].split(')')[0]
            # 沪市前加0， 深市前加1
            if int(stock_code[0]) in [0, 2, 3, 6, 9]:
                if int(stock_code[0]) in [6, 9]:
                    print(stock_code)
                    stock_code_new = '0' + stock_code
                elif int(stock_code[0]) in [0, 2, 3]:
                    print(stock_code)
                    if not int(stock_code[:3]) in [201, 202, 203, 204]:
                        #演示报错，提前输出未知量
                        print(stock_code_new)
                        stock_code_new = '1' + stock_code
                    else:
                        continue
                else:
                    continue
            else:
                continue

            stock_url = 'http://quotes.money.163.com/trade/lsjysj_{}.html'.format(stock_code)
            respones = requests.get(stock_url, headers=headers).text
            soup = bs(respones, 'lxml')
            # 获取起始时间
            start_time = soup.find('input', {'name': 'date_start_type'}).get('value').replace('-', '')
            # 获取结束时间
            end_time = soup.find('input', {'name': 'date_end_type'}).get('value').replace('-', '')
            # 两次访问之间休息1-2秒
            time.sleep(random.choice([1, 2]))
            download_url = "http://quotes.money.163.com/service/chddata.html?code={}&start={}&end={}&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP".format(
                stock_code_new, start_time, end_time)
            data = requests.get(download_url, headers=headers)
            file_name = outfile + '\\{}.csv'.format(stock_code)
            with open(file_name, 'wb') as f:
                # 批量写入数据
                for chunk in data.iter_content(chunk_size=10000):
                    if chunk:
                        f.write(chunk)
            print("{}已下载".format(stock_code))

        except Exception as e:
            print("{}({})下载出错".format(stock_name, stock_code))
            print("错误原因为：",e)



import os


# 获取目录下所有文件，绝对路径
def file_name(file_dir):
    L = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] == '.jpeg':
                L.append(os.path.join(root, file))
    return L

#股票列表
stocklist = []
#可以设置最大页数，截止2021.11.15，有240页
#此处仅使用3页作为例子
max_page = 3
for i in range(max_page):
    url = '''http://1.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112405721872315676919_1566176986516&pn={}
    &pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2&
    fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152
    &_=1566176986517'''.format(i + 1)
    response = requests.get(url).content.decode('utf-8')
    json_text = re.sub(r'jQuery112405721872315676919_1566176986516\(', '', response)[:-2]
    # json_str = re.sub(r'\)', '', response)
    json_text = json.loads(json_text)
    for fi in json_text['data']['diff']:
        stocklist.append([fi['f12'], fi['f14']])

# 下载数据
get_data(stocklist, outfile=r'E:\PycharmProjects\BigDataSight\stockdata')

