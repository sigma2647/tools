# %% 
import pdfplumber
import glob
import os
import pandas as pd
import re
# get current working directory
cwd = os.getcwd()
# get all pdf files in current working directory
pdf_files = sorted(glob.glob(cwd + "/*.pdf"))
# 去除包含"行程单"的文件


# 正则表达式匹配年月日
pattern_date = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')

# 正则表达式匹配价税合计
pattern_total = re.compile(r'价税合计：\d+\.\d+')

# 正则表达式匹配人民币符号
pattern_rmb = re.compile(r'¥\d+\.\d+')

# 正则表达式匹配8位数的发票代码
# pattern_taxnum = re.compile(r'\d{8}')
pattern_taxnum = re.compile(r'(?:\b\d{8}\b)')


# 正则表达式匹配小数点后两位
pattern_decimal = re.compile(r'\d+\.\d{2}')



def pdf2text(file_path):
    pdf = pdfplumber.open(file_path)
    text = pdf.pages[0].extract_text()
    pdf.close()
    return text

def cal_meony(rmb):
    '''
    计算金额
    rmb: 
        rmb[0] = net
        rmb[1] = tax
    '''
    print('进行普通计算')
    net   = float(rmb[0][1:])  # 获取税前价
    tax   = float(rmb[1][1:])  # 获取税额
    print('net:', net)
    print('tax:', tax)
    if net == tax:  # 此情况为免税无需计算税点,直接返回金额
        print('免税')
        return net
    elif net != tax:  # 当税前价和税额不相等时，计算税点
        total = float(rmb[2][1:])
        if abs(total-(net+tax)) < 1:
            return total
    else:
        return 'error'


    # if abs(total-(net+tax)) < 1:

# file = '12213.pdf'
# non = pdf2text(file)
# print(non)
# exit()

def special(text):
    '''
    处理发票中金额没有$
    text: 
    '''
    # 当出现/n时，则认为是一个新的行
    # 获取价格
    rmb = re.findall(pattern_rmb, text)
    text_list = text.split('\n')  # 判断是否是空行
    # 获取列表中包含'合计'的元素
    text_list = [i for i in text_list if '合计' in i]
    list_0 = text_list[0]
    list_1 = text_list[1]
    # 小数点后两位分割16.470.49分成16.47和0.49
    net = float(pattern_decimal.findall(list_0)[0])
    tax = float(pattern_decimal.findall(list_0)[1])
    total = float(pattern_decimal.findall(list_1)[0])
    print('无$进行特殊计算')


    return net, tax, total

for i in pdf_files:
    print(i)
    text = pdf2text(i)
    # 去除空格
    text = text.replace(' ', '')
    # 全角转半角
    text = text.replace('￥', '¥')
    # 正则表达式匹配年月日
    date = pattern_date.findall(text)[0]
    ## 格式化日期
    date = date.replace('年', '-').replace('月', '-').replace('日', '')
    # 匹配税号
    taxnum = pattern_taxnum.findall(text)[0]
    # 正则表达式价税合计（大写)
    money = pattern_total.findall(text)
    # 正则表达式匹配人民币符号
    rmb = pattern_rmb.findall(text)
    # print(rmb)
    if rmb == []:
        net, tax, total = special(text)
    # 计算价税合计
    else:
        total = cal_meony(rmb)
        # 将日期、价税合计写入文件名
    # 将日期、价税合计写入文件名
    # os.rename(i, date + '_' + str(total) + '.pdf') print(date, money, rmb, total)

    # 重命名文件
    os.rename(i, f'{date}发票_{total}元_发票号_{taxnum}.pdf')

