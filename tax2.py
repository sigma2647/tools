# %% 
import pdfplumber
import glob
import os
import pandas as pd
import re

root_dir = os.getcwd()
pdf_lists = sorted(glob.glob(root_dir + "/*.pdf"))


# %% 
# 定义一个类
class Tax:
    def __init__(self, pdf_lists):  # 初始化读取pdf文件

        pdf = pdfplumber.open(pdf_lists)  # 读取pdf文件
        text = pdf.pages[0].extract_text()  # 获取文本
        pdf.close()  # 关闭pdf文件

        # 文本处理
        text = text.replace(' ', '')  # 去除空格
        text = text.replace('￥', '¥')  # 全角转半角
        text = text.replace('：', ':')  # 全角转半角

        self.text = text

    def get_tax_number(self):  # 获取发票号码
        pattern_taxnum = re.compile(r'(?:\b\d{8}\b)')  # 正则表达式获取8位数字
        tax_number = pattern_taxnum.findall(self.text)[0]
        return tax_number

    def get_date(self):  # 获取发票日期
        pattern_date = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
        date = pattern_date.findall(self.text)[0]
        date = date.replace('年', '-').replace('月', '-').replace('日', '')
        return date


    def cal_total(self):
        # 正则表达式匹配价税合计
        pattern_total = re.compile(r'价税合计：\d+\.\d+')
        # 正则表达式匹配人民币符号
        pattern_rmb = re.compile(r'¥\d+\.\d+')
        # 正则表达式价税合计（大写)
        pattern_decimal = re.compile(r'\d+\.\d{2}')

        self.money = pattern_total.findall(self.text)

        if '¥' in self.text:
            print('有人民币符号')
            self.net = float(pattern_rmb.findall(self.text)[0].replace('¥', ''))
            self.tax = float(pattern_rmb.findall(self.text)[1].replace('¥', ''))
            # self.total = str(pattern_rmb.findall(self.text)[2].replace('¥', ''))
            if self.net == self.tax:  # 此情况为免税无需计算税点,直接返回金额
                print('免税')
                # self.total = self.net
                # print(self.total)
                return self.net
            elif self.net != self.tax:  # 当税前价和税额不相等时，计算税点 

                total = self.net + self.tax
                return total
                # print('无符号有税点')
                # rmb = srtpattern_rmb.findall(self.text)
                # # total = float(rmb[2][1:])
                # text_list = self.text.split('\n')  # 判断是否是空行
                # list_0 = text_list[0]
                # list_1 = text_list[1]
                # self.net = float(pattern_decimal.findall(list_0)[0])
                # self.tax = float(pattern_decimal.findall(list_0)[1])
                # self.total = float(pattern_decimal.findall(list_1)[0])
        elif "¥" not in self.text:
            print('无$进行特殊计算')
            # self.net = pattern_decimal.findall(self.text)
            text_list = self.text.split('\n')  # 判断是否是空行
            text_list = [i for i in text_list if '合计' in i]
            list_0 = text_list[0]
            list_1 = text_list[1]
            # 小数点后两位分割16.470.49分成16.47和0.49
            net = float(pattern_decimal.findall(list_0)[0])
            tax = float(pattern_decimal.findall(list_0)[1])
            total = float(pattern_decimal.findall(list_1)[0])


            return total
            # self.net = float(pattern_decimal.findall(self.text)[0])
            # self.tax = float(pattern_decimal.findall(self.text)[1])
            # rmb = re.findall(pattern_rmb, self.text)

            print(text_list)
            # print(self.net)


            # self.total = float(pattern_decimal.findall(self.text)[2])
            # total = self.net + self.tax
            # return total
    def rename(self, root_dir, date, tax_number, total):  # 格式重命名文件
        # print(root_dir, f'{date}发票_{total}元_发票号_{tax_number}.pdf')
        os.rename(i, f'{date}_发票_{total}元_发票号_{tax_number}.pdf')
        pass

# %% 

# tax = Tax(pdf_files[0])
# tax.file_path
# tax.text

for i in pdf_lists:
    tax = Tax(i)  # 创建i个类的实例
    tax_number = tax.get_tax_number()  # 获取发票号码
    date = tax.get_date()
    total = tax.cal_total()  # 计算金额
    # 取两位小数
    total = round(total, 2)
    tax.rename(i, date, tax_number, total)  # 重命名文件

print('发票重命名完成')

exit()

## 以下部分为计算税点的代码
# %% 
import pandas as pd
pdf_lists = sorted(glob.glob("*.pdf"))
## 读取文件名转换为dataframe
pdf_df = pd.DataFrame(pdf_lists)
## 或取文件名中的日期
pdf_df['date'] = pdf_df[0].apply(lambda x: x.split('_')[0])
## 或取文件名中的金额变成浮点型
pdf_df['total'] = pdf_df[0].apply(lambda x: x.split('_')[2].replace('元', ''))
# 变成浮点型
pdf_df['total'] = pdf_df['total'].astype(float)
# 最下面一行

# pdf_df['total'] = pdf_df['file_path'].apply(lambda x: x.split('/')[-1].split('_')[1].split('元')[0])
# 获取总金额
total = round(pdf_df['total'].sum(), 2)
print(pdf_df)
print(total)

pdf_df.to_csv(f'电子发票明细总金额{total}.csv', encoding='utf-8')



