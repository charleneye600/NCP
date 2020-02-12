'''
@author：Billie
更新说明：
1-28 17:00 项目开始着手，spider方法抓取到第一条疫情数据，save_data_csv方法将疫情数据保存至csv文件
1-29 13:12 目标网页文档树改变，爬取策略修改，建立新方法：spider2
1-30 15:00 新建变量national_confirm,存储全国新增确诊数
1-31 15:00 摸鱼，缝缝补补又一天
2-01 15:00 目标网页文档树又改变了，爬取策略修改，建立新方法：spider3，全国数据改用xpath方法查找，全国数据新增“较昨日+”内容显示
2-02 15:00 建立新方法：save_data_main,存储所有日期的全国动态数据到main.csv,复习numpy,pandas
2-03 15:00 建立新方法：make_pic,使用matplotlib绘图
2-09 10:00 建立新方法：__init__,设置全局变量
2-11 14:00 建立新方法：make_chart,使用pyechart绘制图表
'''
import csv
import pandas as pd
import numpy as np
import selenium.webdriver
from selenium.webdriver.chrome.options import Options
import threading
import os
import matplotlib.pyplot as plt
from pyecharts.charts import Line,Bar,Grid
from pyecharts import options as opts
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot# 使用 snapshot-selenium 渲染图片
from pyecharts.globals import ThemeType# 内置主题类型可查看 pyecharts.globals.ThemeType


class Epidemic():
    def __init__(self):
        self.base_url="https://news.qq.com/zt2020/page/feiyan.htm"
        self.timeNum = 0#数据获取时间
        self.icbar_confirm = 0#全国确诊数
        self.icbar_confirm_a = 0#全国新增确诊
        self.icbar_suspect = 0#全国疑似
        self.icbar_cure = 0#全国治愈
        self.icbar_dead = 0#全国死亡
        self.dataDic = dict()#键为省名，值为省的具体数据
    def spider(self):#2/1目标网页已改变
        global timeNum, provinceDic
        # 无窗口弹出操作
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver=selenium.webdriver.Chrome(options=options)
        driver.get(self.base_url)
        self.timeNum=driver.find_element_by_xpath('//*[@id="charts"]/div[2]/div[1]/div/p[1]').text[2:]#实时
        self.icbar_confirm=driver.find_element_by_xpath('//*[@id="charts"]/div[2]/div[2]/div[1]/div[2]').text#全国确诊数
        icbar_confirm_add=driver.find_element_by_xpath('//*[@id="charts"]/div[2]/div[2]/div[1]/div[1]').text#全国确诊数add
        self.icbar_suspect=driver.find_element_by_xpath('//*[@id="charts"]/div[2]/div[2]/div[2]/div[2]').text#疑似病例数
        icbar_suspect_add=driver.find_element_by_xpath('//*[@id="charts"]/div[2]/div[2]/div[2]/div[1]').text#疑似病例数add
        self.icbar_cure=driver.find_element_by_xpath('//*[@id="charts"]/div[2]/div[2]/div[3]/div[2]').text#治愈人数
        icbar_cure_add=driver.find_element_by_xpath('//*[@id="charts"]/div[2]/div[2]/div[3]/div[1]').text#治愈人数add
        self.icbar_dead=driver.find_element_by_xpath('//*[@id="charts"]/div[2]/div[2]/div[4]/div[2]').text#死亡人数
        icbar_dead_add=driver.find_element_by_xpath('//*[@id="charts"]/div[2]/div[2]/div[4]/div[1]').text#死亡人数add
        self.icbar_confirm_a=driver.find_element_by_xpath('//*[@id="charts"]/div[2]/div[2]/div[1]/div[1]/span').text.strip("+")
        self.dataDic["全国"] = ["全国", self.icbar_confirm, self.icbar_cure, self.icbar_dead, self.icbar_confirm_a, self.icbar_suspect]
        print("\n{}\n全国确诊：{}\n疑似病例：{}\n治愈人数：{}\n死亡人数：{}\n".format(self.timeNum, self.icbar_confirm+" "+icbar_confirm_add,self.icbar_suspect+" "+icbar_suspect_add, self.icbar_cure+" "+icbar_cure_add, self.icbar_dead+" "+icbar_dead_add))
        hubei=driver.find_elements_by_css_selector('div[class="placeItemWrap current"]')#湖北省的数据集
        wuhan=driver.find_elements_by_css_selector("div[city='武汉']")#武汉市的数据集
        elprovince = driver.find_elements_by_css_selector('div[class="placeItemWrap"]')#其他省的数据集
        abroad = driver.find_elements_by_css_selector('div[class="clearfix placeItem placeArea no-sharp abroad"]')#海外国家的数据集
        tplt = "{1:{0}<10}\t{2:{0}<15}\t{3:{0}<15}\t{4:{0}<15}\t{5:{0}<15}"
        print(tplt.format(chr(12288),"地区","新增确诊","确诊人数","治愈人数","死亡人数",))
        places = hubei + wuhan + elprovince + abroad#所有的地区的数据列表合集
        for p in places:#查找目标，name\add\confirm\heal\dead
            place=p.find_element_by_css_selector("h2").text#湖北/武汉/国内/海外地区
            try:add=p.find_element_by_css_selector("div[class='add ac_add ']").text#国内新增确诊
            except:
                if place=="武汉":add = p.find_element_by_css_selector("div[class='ac_add ']").text#武汉地区新增确诊
                else:add=""#海外地区无数据
            try:confirm=p.find_element_by_css_selector("div[class='confirm']").text#国内累计确诊
            except:
                if place=="武汉":confirm=p.find_elements_by_css_selector("div")[1].text#武汉累计
                else:confirm = p.find_elements_by_css_selector("div")[0].text#海外累计确诊
            try:heal=p.find_element_by_css_selector("div[class='heal']").text#国内治愈人数
            except:
                if place=="武汉":heal=p.find_elements_by_css_selector("div")[2].text#武汉治愈人数
                else:heal = p.find_elements_by_css_selector("div")[1].text#海外治愈
            try:dead=p.find_element_by_css_selector("div[class='dead']").text#国内死亡
            except:
                if place=="武汉":dead = p.find_elements_by_css_selector("div")[3].text #武汉死亡人数
                else:dead = p.find_elements_by_css_selector("div")[2].text#海外死亡人数
            print(tplt.format(chr(12288),place,add,confirm,heal,dead,))
            self.dataDic[place]=[place,confirm,heal,dead,add]#向字典添加数据
    def save_data_csv(self,filepath,filename):#存储到allcsv\dailycsv中的csv文件
        # filename="_".join(time.split(":"))
        dataList=list(self.dataDic.values())
        with open(filepath+"//"+filename+".csv","w",newline="") as f:
            writer=csv.writer(f)
            writer.writerow(["地区","确诊人数","治愈人数","死亡人数","新增确诊","疑似病例"])
            for i in dataList:writer.writerow(i)#写入各个地区的数据
            writer.writerow([self.timeNum])#最后一行附上截至时间
            f.close()
    def save_data_main(self,filename):#存储所有日期的全国动态数据
        allfile=os.listdir("dailycsv")#所有的目标文件
        columns=["确诊人数", "治愈人数", "死亡人数", "新增确诊", "疑似病例"]#df参数1：main.csv的行索引
        index = [file[:-4] for file in allfile]#df参数2：main.csv的列索引,索引为去掉'.csv'的文件名
        data = []#df参数3：写入df的数据
        for file in allfile:#file: 2020-xx-xx xx xx xx.csv
            with open("dailycsv//"+file,"r") as f:#打开目标文件
                d=list(csv.reader(f))#读取目标文件数据，返回list
                data.append(d[1][1:])#目标数据是第一行的全国数据，且从第二列开始
                f.close()
        df=pd.DataFrame(data,index=index,columns=columns)#创建dataframe对象
        df.to_csv(filename,encoding="gbk")#将dataframe对象保存至csv文件
    def make_chart(self,filename):#pyechart
        #变量此时的数据类型:<class 'numpy.ndarray'>，需转化为列表
        (time,confirm,heal,dead,add,suspect)=np.loadtxt(filename,\
                                            skiprows=1,\
                                            dtype='str',\
                                            delimiter=',',\
                                            usecols=(0,1,2,3,4,5),\
                                            unpack=True)
        #新建图表
        chart =Line()#init_opts=opts.InitOpts(theme=ThemeType.LIGHT)
        #设置图表标题
        chart.set_global_opts(title_opts={"text": "全国NCP疫情趋势图", "subtext": self.timeNum})#
        #设置x,y轴
        chart.add_xaxis([i[-4:] for i in time])
        chart.add_yaxis("确诊", list(confirm),symbol=" ",is_symbol_show=True)#,is_connect_nones=False
        chart.add_yaxis("治愈", list(heal))
        chart.add_yaxis("死亡", list(dead))
        chart.add_yaxis("新增确诊", list(add))
        chart.add_yaxis("疑似病例", list(suspect))
        chart.width=100
        chart.page_title="NCP疫情动态"
        chart.theme="black"
        #保存为本地文件
        # render 会生成本地 HTML 文件，默认会在当前目录生成 render.html 文件，bar.render("mycharts.html")
        make_snapshot(snapshot, chart.render("main.html"), "main.png")
        os.startfile(os.getcwd()+"\\main.html")#打开文件

    def main(self):
        ''''''
        self.spider()#获取疫情实时动态信息
        self.save_data_csv(filepath="allcsv",\
                           filename=self.timeNum[3:22].replace(":"," "))#存入allcsv文件
        self.save_data_csv(filepath="dailycsv",\
                           filename=self.timeNum[3:22].replace(":"," ")[:10])#存入dailycsv文件
        self.save_data_main(filename="main.csv")

        self.make_chart(filename="main.csv")
        # self.make_chart2(filename="main.csv")
        #设定运行间隔时间
        global timer
        timer=threading.Timer(1000,self.main)
        timer.start()
if __name__ == '__main__':
    billie=Epidemic()
    billie.main()

