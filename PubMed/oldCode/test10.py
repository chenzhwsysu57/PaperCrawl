keywords = 'Pediatric neurosurgery'

# -*- coding: utf-8 -*-
from tqdm import tqdm

from timevar import savetime
import time 
import random
from time import sleep
from bs4 import BeautifulSoup


import random
import re
import sqlite3
import time
import urllib
import urllib.error
from urllib import request

import eventlet
import xlwt

from PubMed.old.geteachinfo import readdata1
from timevar import savetime
import glob

file_list = glob.glob('./document/neurosurgery/*.pdf')
number_list = []

# Loop through the original list and extract the numbers
for file in file_list:
    # Split the string by '/' and then by '.' to isolate the number
    number = file.split('/')[-1].split('.')[0]
    number_list.append(number)


class Search_param(str):
    """
    搜索参数管理类，用于拼接在baseurl之后

    可以由generate方法encode生成初次检索所需的URL后缀
    例如：”?term=alzheimer%27s+disease“
    可以附加一些调整网页的属性

    TODO: 按日期搜索，
    2020.1.1 - 2020.1.31: 
    https://pubmed.ncbi.nlm.nih.gov/?term=computer+science&filter=dates.2020%2F1%2F1-2020%2F1%2F31

    2024.5.1 - 2024.5.31
    https://pubmed.ncbi.nlm.nih.gov/?term=computer+science&filter=dates.2024%2F5%2F1-2024%2F5%2F31
    """
    def __init__(self, keywords:str):
        self.search_keywords = {}
        self.search_keywords['term'] = keywords.strip()

    def gen_search_param(self) -> str:
        # encode url生成request需要的url
        return urllib.parse.urlencode(self.search_keywords)

    def specify_web_size(self, size: int):
        # 调整 搜索页面的大小
        self.search_keywords['size'] = size

    def specify_any_param(self, key: str, value):
        """
        针对任意参数进行调整, 需要提供合适的键值对，默认不存在
        目前观察到的有：sort(date, pubdate, fauth, jour), sort_order(asc) 更多参数请查看pubmed的搜索URL
        :param key: url链接需要添加的键
        :param value: url链接中键对应的值
        :return:
        """
        self.search_keywords[key] = value

def spider_pubmed_paper_metadata(parameter: str = "computer science", startpage: int = 1,  endpage: int = 12):
    """ return: metadata of papers
        爬虫函数主体 
        startpage 是从搜索结果第几页起爬
        endpage 是搜索结果第几页结束爬
        返回： datalist: list = [] 每个元素是一篇论文的情况
        每个元素的内容： 
        ```
        0: document title
        1: author list
        2: journal 
        3: doi 
        4: PMID
        5: freemark, 是否free, 2 是有原文的
        6: reviewmark, 是否 review
        ```
    """
    datalist = [] # startpage 到 endpage 的页中的论文列表


    baseurl = "https://pubmed.ncbi.nlm.nih.gov/"
    url=""
    header={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32"}

    # 先获取所有搜索结果：
    result_all = -1

    # 下列正则表达式用来搜索
    findlink_PMID = re.compile(r'<span class="citation-part".*>(\d+)<\/span>')  # 提取PMID号，作为下载的地址
    findlink_journal = re.compile(r'journal-citation">(.*?) doi:.*?\.[ <]')  # 查找期刊名称
    findlink_doi = re.compile(r'journal-citation">.*? (doi:.*?\.)[ <]')  # 查找文献doi
    findlink_title = re.compile(r'<a class="docsum-title".*?">.*?([A-Z0-9].*?)[.?]', re.S) # 提取文章的title，含有</b>符号。每页有50个文章的title
    findlink_auto_info = re.compile(r'full-authors">(.*?)<\/span>')  # 查找作者名称信息
    findlink_FREE_PMC_MARK = re.compile(r'<span class="free-resources.*?>(.*)\.<')  # 提取free pmc article标志
    findlink_review = re.compile(r'citation-part">Review.<\/span>')  # 查找文献review标签

    progress_bar = tqdm(total=endpage - startpage)
    for i in range(startpage, endpage):

        # [1] 开始遍历每一页结果，一共 page 页最大pagemax页
        

        # [2] 用指定的参数， get 的方式获取 pubmed 的搜索结果 
        url=baseurl+"?"+ parameter + "&page=" + str(i)
        request=urllib.request.Request(url,headers=header)
        response=urllib.request.urlopen(request)
        # print(f'\033[1;35m url is {url}\033[0m')
        html=response.read()

        content = BeautifulSoup(html, "html.parser")
        # [3] 计算 result_all 是 <span class="value">498,730</span> 中的 498730。网页展示 498,730 results
        result_all = int(str(content.find_all("span", class_="value")[0])[20:-7].replace(',', '')) 
        

        # [3] 把一个页面的 50 条结果全部返回成一个 list
        #data = traverse(html)
        data = []
        # print(f'\033[1;35m len of item is {len(content.find_all("div", class_="docsum-content"))}\033[0m')
        for item in content.find_all("div", class_="docsum-content"):
            ''' 获取 PMID, 作者, 期刊, doi, title, 是否free, 是否 review '''
            item = str(item)
            
            # 获取 PMID
            PMID = re.findall(findlink_PMID, item)[0]

            # 获取作者
            authorlist = re.search(findlink_auto_info, item)
            if authorlist != None:
                authorlist = authorlist.group(1)
            else:
                authorlist = ''

            # 获取期刊
            journal = re.search(findlink_journal, item)  
            if journal == None:
                journal = ''
            else:
                journal = journal.group(1)


            # 获取 doi
            doi = re.search(findlink_doi, item)  # 少数文献是没有doi号的，直接用item[0]会导致index超出
            if doi == None:
                doi = ''
            else:
                doi = doi.group(1)

            # 获取 title
            doctitle = re.findall(findlink_title, item)[0]
            doctitle = doctitle.replace("-/-", '')
            doctitle = re.sub(r"<.+?>", '', doctitle)

            # freemark flag: 0，不是免费文件无原文，1 是free article无原文， 2 是有pmc原文
            freemark = re.findall(findlink_FREE_PMC_MARK, item)
            if len(freemark) == 0:
                freemark = '0'
            else:
                if len(freemark[0]) == 16:
                    freemark = '2'
                else:
                    freemark = '1'

            # 1 表示文章类型是 review
            reviewmark = re.search(findlink_review, item)
            # print(reviewmark.group())
            if reviewmark == None:
                reviewmark = '0'
            else:
                reviewmark = '1'

            temp = []
            temp.append(doctitle)
            temp.append(authorlist)
            temp.append(journal)
            temp.append(doi)
            temp.append(PMID)
            temp.append(freemark)
            temp.append(reviewmark)
            data.append(temp)

        progress_bar.update(1)  # 更新进度条
        datalist.extend(data) # 直接增加到datalist里， 每个元素就是一篇论文的情况
        sleep(random.randint(0, 2))
    progress_bar.close()
    return datalist

def download_pubmed_pdf_using_paper_metadata(metadata):
    # metadata 中没有 PMCID，只有PMID。下面获取PMCID
    baseurl = "https://pubmed.ncbi.nlm.nih.gov/"  # baseurl和之前的搜索页面一致
    PMID = str(metadata[4])

    # 检查 PMID 是否已存在：
    file_list = glob.glob('./document/neurosurgery/*.pdf')
    number_list = []

    # Loop through the original list and extract the numbers
    for file in file_list:
        # Split the string by '/' and then by '.' to isolate the number
        number = file.split('/')[-1].split('.')[0]
        number_list.append(number)
        if PMID in number_list:
            return None

    url = baseurl + PMID
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32"}
    request = urllib.request.Request(url, headers=header)
    html = ""
    response = urllib.request.urlopen(request)
    html = response.read()
    content = BeautifulSoup(html, "html.parser")
    heading = content.find_all('div', class_="full-view", id="full-view-heading")
    heading = str(heading)  # heading是一个包含文章大部分信息的标签
    PMCID = re.search(r'(PMC\d+)\n', heading)  # 获取PMCID用于后续的自动下载
    PMCID = PMCID.group(1)
    # 这一页包括了PMCID和全文等其他部分。但在这里，只需要PMCID就能下载到PDF

    # 尝试直接从 pubmed 下载

    '''
    
    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8022506/pdf/peerj-cs-07-441.pdf
    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8022506/pdf

    29702967
    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC29702967/
    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC36091982/pdf

    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7319935/pdf/main.pdf 打得开, PMID 是 32599201

    PMID 36091982， 题目，Automatic computer science domain multiple-choice questions generation based on informative sentences
    PMCID：
    '''

    downpara = "pmc/articles/" + PMCID + "/pdf"
    baseurl = "https://www.ncbi.nlm.nih.gov/"
    url = baseurl + downpara
    print(f"\033[1;35m[I] pdf url: {url}\033[0m", end = ".")
    header={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32"}
    request=urllib.request.Request(url,headers=header)
    html=""
    response = urllib.request.urlopen(request, timeout=60)
    html = response.read()
    # print("%s.pdf" % metadata[0], "从目标站获取pdf数据成功")
    return html

def fetch_pdf_urls_from_pubmed(keyword = 'computer science', startpage = 1, endpage = 1000):
    search_param = Search_param(keyword)
    metadatas = spider_pubmed_paper_metadata(search_param.gen_search_param(), startpage = startpage, endpage = endpage)
    return metadatas

metadatas = fetch_pdf_urls_from_pubmed(keyword = keywords)
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

length = len(metadatas)
i = 0
for metadata in metadatas:
    print(f'{i}/{length}', end = ',')
    try:
        pdfstream = download_pubmed_pdf_using_paper_metadata(metadata)
        if pdfstream != None:
            savepath = f"./document/neurosurgery/{metadata[4]}.pdf"  # 这里用 PMID 存文件
            file = open(savepath, 'wb')
            file.write(pdfstream)
            file.close()
            print('success', end = '\n')
    except Exception as e:
        # 将异常信息写入日志文件
        logging.error(f"Error: {e}, PMID: {metadata[4]}")
        print('\n')
    i = i + 1