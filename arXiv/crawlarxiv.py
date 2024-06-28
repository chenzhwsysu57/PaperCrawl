# -*- coding: utf-8 -*-
import argparse
import sys
import urllib.request
import feedparser
import logging
logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')
# 创建解析器
parser = argparse.ArgumentParser(description='Process some integers.')
import os
# 添加命令行参数
parser.add_argument('--endpage', type=int, help='The last page to process')
parser.add_argument('--keywords', type=str, help='The keywords to search for')
parser.add_argument('--savedir', type=str, help='The dir where you store pdfs')
# 解析命令行参数
args = parser.parse_args()

# 打印解析后的参数
# print(f"accepted args: endpage = {args.endpage}, keywords = '{args.keywords}'")
# sys.exit()
keywords = args.keywords
endpage = args.endpage
savedir = args.savedir

keywords_list = ['anaesthesiology', 'Anesthesia', 'Anesthesiologist', 'Sedation', 'General anesthesia', 'Regional anesthesia', 'Epidural anesthesia', 'Spinal anesthesia', 'Local anesthesia', 'Conscious sedation', 'Endotracheal tube', 'Laryngeal mask airway (LMA)', 'Intravenous (IV) catheter', 'Anesthetic machine', 'Pulse oximeter', 'Blood pressure cuff', 'Ventilator', 'Intubation', 'Extubation', 'Mask ventilation', 'Consciousness monitor', 'Intraoperative monitoring', 'Preoperative evaluation', 'Postoperative care', 'Anesthetic drugs', 'Muscle relaxant', 'Analgesic', 'Neuromuscular blockade', 'Laryngoscopy', 'Bronchoscopy', 'Arterial line', 'Central venous catheter', 'Hypnotic', 'Recovery room', 'Post-anesthetic care unit (PACU)', 'Capnography', 'Vasoactive medications', 'TIVA (total intravenous anesthesia)', 'Anaphylaxis', 'Epidural analgesia', 'Intrathecal anesthesia', 'MAC (monitored anesthesia care)', 'Ambulatory anesthesia', 'Complication', 'Local anesthetic', 'Neuroleptic anesthesia', 'Sedative-hypnotic', 'Fiberoptic intubation', 'Hemodynamic monitoring', 'Nerve block', 'Pain management', 'Perioperative care', 'Postdural puncture headache', 'Reversal agent', 'Spinal tap', 'Supraventricular tachycardia (SVT)', 'Vasopressor', 'Ventilation-perfusion (V/Q) scan', 'Conscious sedation', 'Intradermal', 'Intraperitoneal', 'Lidocaine', 'Methohexital', 'Muscle relaxant', 'Nondepolarizing agent', 'Narcotic', 'Nitrous oxide', 'Obstructive sleep apnea', 'Orotracheal', 'Respiration', 'Succinylcholine', 'Endotracheal', 'Epidural', 'Hypoxemia', 'Laryngoscope', 'Neuromuscular', 'Pneumothorax', 'Subcutaneous', 'Apnea', 'Bradycardia', 'Circulation', 'Dyspnea', 'Intraoperative', 'Narcotic', 'Ophthalmic', 'Postoperative', 'Preanesthetic', 'Analgesia', 'Bilevel positive airway pressure (BiPAP)', 'Cerebrospinal fluid', 'Cricoid pressure', 'Dissociative anesthesia', 'Exhalation', 'Hemoglobin', 'Intramuscular', 'MAC (minimum alveolar concentration)', 'Neuromuscular blockade', 'Oxygenation', 'Postanesthesia recovery', 'Preanesthesia', 'Sevoflurane']

import os

for keywords in keywords_list[::-1]:
    dir_name = f"downloaded/" + savedir     #你需要检查的目录名
    print(f"\033[1;34m keywords...{keywords} \033[0m")
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)     #如果目录不存在，则创建新目录

    base_url = 'http://export.arxiv.org/api/query?'

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

        def gen_query(self) -> str:
            return urllib.parse.urlencode(self.search_keywords)[5:]
        
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

    def save_tex(tex_url, headers = None):
        header={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32"}
        request=urllib.request.Request(tex_url,headers=header)
        html=""
        response = urllib.request.urlopen(request, timeout=60)
        html = response.read()
        return html

    def save_pdf(pdf_url, herders = None):
        header={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32"}
        request=urllib.request.Request(pdf_url,headers=header)
        html=""
        response = urllib.request.urlopen(request, timeout=60)
        html = response.read()
        return html

    # print(Search_param(keywords).gen_query())
    start = 0  # retreive the first 5 results
    max_results = endpage
    search_query = "all:" + Search_param(keywords).gen_query()

    query = f'search_query={search_query}&start={start}&max_results={max_results}'

    # print(query)

    response = urllib.request.urlopen(base_url + query).read()
    feed = feedparser.parse(response)
    # print("*********************")
    # print('Feed title: %s' % feed.feed.title)
    # print('Feed last updated: %s' % feed.feed.updated)
    # print('totalResults for this query: %s' % feed.feed.opensearch_totalresults)
    # print('itemsPerPage for this query: %s' % feed.feed.opensearch_itemsperpage)
    # print('startIndex for this query: %s' % feed.feed.opensearch_startindex)
    # print("*********************")
    i = 1
    length = len(feed.entries)
    for entry in feed.entries:
        print(f'{i}/{length}', end = ',', flush=True)
        i += 1
        arxiv_id = entry.id.split('/abs/')[-1]
        published = entry.published
        title = entry.title
        author_string = entry.author
        try:
            author_string += ' (%s)' % entry.arxiv_affiliation
        except AttributeError:
            pass
        last_author = author_string


        # 获取  link
        abs_link = ""
        pdf_link = ""
        tex_link = ""
        try:
            for link in entry.links:
                if link.rel == 'alternate':
                    abs_link = link.href
                elif link.title == 'pdf':
                    pdf_link = link.href
            tex_link = abs_link.replace("abs", "src")

            # 下载 pdf
            print(f"\033[1;35m fetching...{pdf_link} \033[0m")
            pdf_stream = save_pdf(pdf_link)
            savepdfpath = dir_name +"/"+ arxiv_id + ".pdf"
            file = open(savepdfpath, 'wb')
            file.write(pdf_stream)
            file.close()
            # print(savepdfpath)
            # # 下载 tex
            # tex_stream = save_tex(tex_link)
            # savetexpath = dir_name +"/"+ arxiv_id + ".tar.gz"
            # file = open(savetexpath, 'wb')
            # file.write(tex_stream)
            # file.close()
            # print('success')
        except  Exception as e:
            logging.error(f"Error: {e}, arxivid: {arxiv_id}")