# -*- coding: utf-8 -*-
from dataclasses import dataclass
import logging
from grobid_client.grobid_client import GrobidClient
import argparse
import sys
import concurrent
import concurrent.futures
from bs4 import BeautifulSoup
import glob
import os
from tqdm import tqdm
from multiprocessing import current_process
# 创建解析器
parser = argparse.ArgumentParser(description='Process some integers.')

# 添加命令行参数
parser.add_argument('--engine', default="grobid",
                    type=str, help='engine to parse pdf')
parser.add_argument('--config', default="./config.json",
                    type=str, help='config file')
parser.add_argument('--service', default="fulltext",
                    type=str, help='function to perform')
parser.add_argument('--input_path', default="./temp",
                    type=str, help='input path for pdf folder.')
parser.add_argument('--output_path', default="./output", type=str,
                    help='output path for folder. if not exist, would create')
parser.add_argument('--worker', default=10, type=int,
                    help='maximum worker number')


# 解析命令行参数
args = parser.parse_args()

# 打印解析后的参数
print(
    f"accepted args: \ninput_path{args.input_path}\nkeywords = '{args.output_path}'")
# sys.exit()


client = GrobidClient(config_path="./config.json")
''' 
processFulltextDocument
processHeaderDocument
processReferences
processCitationList
processCitationPatentST36
processCitationPatentPDF
'''

logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')


def grobid_pdf_fulltext_to_txt(
        config_path: str = "./config.json",
        pdf_path: str = "./test/abc/1.pdf",
        args: argparse.ArgumentParser.parse_args = None):

    ''' 调用 process_pdf 去处理一个 pdf 文件，存储 output/[pdf文件名].txt 到指定的路径

    需要被并发执行，所以只能指定一条传入pdf文件路径。output用于拼接和创建新的存储路径

    对于出错的情况写入log file

    保存txt的路径： output_path 拼接 pdf名字.txt
    '''
    service = "processFulltextDocument"

    outname = os.path.join(args.output_path,
                           os.path.basename(pdf_path)[:-4] + ".txt")
    
    if os.path.exists(outname) and os.path.getsize(outname) > 0:
        print(f"\033[1;33mW: skipping {outname} as it exist...\033[0m")
        return
    print(f'\033[1;37m[Info] processing {pdf_path}')

    client = GrobidClient(config_path=config_path)
    pdf_path, status, raw_tei = client.process_pdf(
        service=service,
        pdf_file=pdf_path,
        generateIDs=False,
        consolidate_header=True,
        consolidate_citations=False,
        include_raw_citations=False,
        include_raw_affiliations=False,
        tei_coordinates=False,
        segment_sentences=False
    )

    if status != 200 or TEIFile(raw_tei).text is None:
        logging.error(f"{pdf_path} error!")
        print(f"\033[1;31m[Err] {status} {pdf_path}\033[0m")
        return
    print(f"\033[1;32m[OK] {pdf_path}\033[0m")

    if not os.path.exists(outname):
        print(f"\033[1;32m[INFO] creating {outname}.\033[0m")
        os.makedirs(os.path.dirname(outname), exist_ok=True)
        with open(outname, 'w') as file:
            file.write(TEIFile(raw_tei).text)
    else:
        print(f"\033[1;33m[W] {outname} already exists. return.\033[0m")

    return


def grobid_pdf_fulltext_to_txt_with_progress_bar(config_path, pdf_path, args, progress_bar):

    grobid_pdf_fulltext_to_txt(config_path, pdf_path, args)
    progress_bar.update(1)
    return


def fulltext_tei_to_txt(tei_path):
    ''' not done yet '''
    tei = TEIFile(tei_path)
    paper_title = tei.title
    paper_abstract = tei.abstract
    paper_doi = tei.doi
    paper_text = tei.text


def elem_to_text(elem, default=''):
    if elem:
        return elem.getText()
    else:
        return default


def read_tei(tei_file):
    with open(tei_file, 'r') as tei:
        soup = BeautifulSoup(tei, 'lxml')
        return soup

def parse_tei(tei):
    return BeautifulSoup(tei, 'lxml')

@dataclass
class Person:
    firstname: str
    middlename: str
    surname: str


class TEIFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.soup = parse_tei(filename)
        self._text = None
        self._title = 'title not detected!'
        self._abstract = 'abstract not detected!'

    @property
    def doi(self):
        idno_elem = self.soup.find('idno', type='DOI')
        if not idno_elem:
            return ''
        else:
            return idno_elem.getText()

    @property
    def title(self):
        if not self._title:
            self._title = self.soup.title.getText()
        return self._title

    @property
    def abstract(self):
        if not self._abstract:
            abstract = self.soup.abstract.getText(
                separator=' ', strip=True)
            self._abstract = abstract
        return self._abstract

    @property
    def authors(self):
        authors_in_header = self.soup.analytic.find_all('author')

        result = []
        for author in authors_in_header:
            persname = author.persname
            if not persname:
                continue
            firstname = elem_to_text(
                persname.find("forename", type="first"))
            middlename = elem_to_text(
                persname.find("forename", type="middle"))
            surname = elem_to_text(persname.surname)
            person = Person(firstname, middlename, surname)
            result.append(person)
        return result

    @property
    def text(self):
        if not self._text:
            divs_text = []
            for div in self.soup.body.find_all("div"):
                # div is neither an appendix nor references, just plain text.
                if not div.get("type"):
                    div_text = div.get_text(separator=' ', strip=True)
                    divs_text.append(div_text)

            plain_text = " ".join(divs_text)
            self._text = plain_text
        return self._text

    def write_txt(self, dest: str = None):
        if not os.path.exists(dest) or os.path.getsize(dest) == 0:
            with open(dest, 'w') as file:
                file.write(self.text)


def main():
    # files = glob.glob(os.path.join(args.input_path.rstrip(os.sep), "*.pdf"))
    files = glob.glob(os.path.join(args.input_path, "*.pdf"))

    with tqdm(total=len(files), desc="handling pdfs") as progress_bar:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(
                grobid_pdf_fulltext_to_txt_with_progress_bar, args.config, file, args, progress_bar) for file in files]
            concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()
