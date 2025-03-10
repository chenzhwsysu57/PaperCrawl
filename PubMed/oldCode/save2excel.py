# -*- coding: utf-8 -*-
import sqlite3
from time import sleep
import os

import xlwt
import sys


def save2excel(dbpath):
    savepath = './pudmed-%s.xls' % savetime
    if os.path.exists(savepath):
        print(f"指定的保存条目文件{savepath[2:]}已存在，文件重复\n\n")
        confirm = str(input(f"是否删除原有的{savepath[2:]}文件, y or n\n"))
        if confirm == "y" or "yes":
            os.remove(savepath)
        else:
            print("无法保存成excel文件， 文件名重复冲突\n")
            exit(-1)
    tablename = 'pubmed%s' % savetime
    try:
        try:
            conn = sqlite3.connect(dbpath)
            cursor = conn.cursor()
            sql = '''SELECT * FROM %s''' % tablename
            cursor.execute(sql)
            savedata = cursor.fetchall()
            # print(savedata)
            conn.commit()
            cursor.close()
            print("读取最终数据库信息成功")
        except:
            print("读取数据库生成excel时失败，请检查数据库")
        workbook = xlwt.Workbook(encoding="utf-8", style_compression=0)
        worksheet = workbook.add_sheet("pumedsoso", cell_overwrite_ok=True)
        col = (
        '序号', '文献标题', '作者名单', '期刊年份', 'doi', 'PMID', 'PMCID', '摘要', '关键词', '作者单位', '是否有免费全文', '是否是review', '保存路径')
        for i in range(len(col)):
            worksheet.write(0, i, col[i])
        for i in range(len(savedata)):
            print("保存第%d条到excel" % (i + 1))
            savedata[i] = list(savedata[i])
            # print(savedata[i])
            for j in range(len(savedata[i])):
                savedata[i][j] = str(savedata[i][j])
                if j == 10:
                    savedata[i][j] = savedata[i][j].replace('2', '是').replace('1', '否').replace('0', '否')
                if j == 11:
                    savedata[i][j] = savedata[i][j].replace('1', '是').replace('0', '否')
                worksheet.write(i + 1, j, savedata[i][j])
        workbook.save(savepath)
        print("\n爬取数据库信息保存到excel成功\n")
    except IOError:
        print("保存excel 文件IO异常")
    except Exception:
         print("爬取数据库信息保存到excel失败\n")

def gettable(dbpath):
    try:
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()
        cursor.execute("SELECT name from sqlite_master where type='table' order by name")
        tablelist = cursor.fetchall()
        conn.commit()
        cursor.close()
        for i in range(len(tablelist)):
            tablelist[i] = tablelist[i][0]
        del tablelist[-1]
        return tablelist
    except:
        print("数据库查询出错，请检查数据库")

if __name__ == "__main__":
    global dbpath
    dbpath='pubmedsql'
    # save2excel(dbpath)

        # for i in range(len(result)):
        #
        #     time.sleep(random.randint(1,5))

    tablelist = gettable(dbpath)
    if tablelist == None:
        print("目标数据库不存在或者内容为空，请检查数据库，即将退出")
        sleep(1)
        sys.exit(-1)
    print("\n")
    x = 99
    while x != 0:
        sleep(0.5)
        print("当前目录数据库中含有以下table(数据表格)pubmed后面的数字为生成时精确到秒的时间\n", '----' * 20, '\n')
        for i in range(len(tablelist)):
            print("[%d]%s  " % (i + 1, tablelist[i]))
        print("\n")
        print('----' * 20)
        try:
            x = int(input("\n请输入你想要导出生成excel表格的数据库table编号，如1,2,3,4，输入0退出程序，注意不要输入上面的pubmedxxxxx编号\n\n"))
        except ValueError:
            print('----' * 20, '\n')
            print("输入错误，如1,2,3,4，输入0退出程序，注意不要输入上面的pubmedxxxxx编号\n\n")
            print("重新输入，下一个循环")
            sleep(3)
            print('----' * 20, '\n')

            continue
        if x == 0:
            print("欢迎使用，程序即将结束")
            sleep(0.5)
            break
        index = tablelist[x - 1]
        # print(index)
        global savetime
        savetime = index[6:]
        # print(savetime)
        save2excel(dbpath)
        print("此次保存执行完成，下一个循环")
        sleep(3)
        print('----' * 20,"\n")

    os.system("pause")



