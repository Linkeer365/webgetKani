# 这次用一下多线程, 爬一下京阿尼的笨蛋日常
# import profile

from multiprocessing import Pool,cpu_count,Process,freeze_support

import selenium
from selenium.webdriver.support.ui import Select # 处理下拉框用的
import os
geko_path='C:\Program Files\Mozilla Firefox\geckodriver.exe'
driver=selenium.webdriver.Firefox(executable_path=geko_path)
from time import sleep,time
src_dir='D:/京都笨蛋日常2'
import re
if not os.path.exists(src_dir):
    os.mkdir(src_dir)
# 注释10-58, 单元测试

start_time=time()

root_url='http://www.kyotoanimation.co.jp/staff/anibaka/blog/'

driver.get(root_url)
# 日期在下拉框中,
dates_options=Select(driver.find_element_by_xpath('//select[@name="archive-dropdown"]')).options
dates=[] # 这个dates精确到月
# 下拉框第一个不要


# m3是最快的...吧
# def m1():
#     for date_option in dates_options[1:]: # 这部分有空优化一下, 太慢了
#         raw_date=date_option.text
#         year=raw_date.split('年')[0]
#         month=raw_date.split('年')[-1].split('月')[0]
#         if int(month)<10:
#             month='0'+month
#         formatted_date=year+month
#         # dates.append(formatted_date)

# def m2():
#     for dates_option in dates_options[1:]:
#         raw_date=dates_option.text
#         year=raw_date[0:4] # 年份4位数, 相减正好是4
#         month=raw_date[5:len(raw_date)-1] # "年" 这个字符永远出现在第4位上面(0起), 所以从5后面全是, 最后一个是"月"子要排除
#         print(year,month)
#         formatted_date=year+month.zfill(2) # 这一招用0补齐, 格式就是这样

# def m3():
for dates_option in dates_options[1:]:
    raw_date=dates_option.text[:-1] # 最后一个月字去掉
    year,month=raw_date.split('年')
    # print(year,month)
    formatted_date=year+month.zfill(2) # 这一招用0补齐, 格式就是这样
    dates.append(formatted_date)

page_urls=[root_url+'?m='+date for date in dates]
new_page_urls=[]

# 这个可以考虑用多线程试试, 遍历具体日子这个
for page_url in page_urls:
    driver.get(page_url)
    day_elems=driver.find_elements_by_xpath('//a[contains(@href,"{}") and @title]'.format(page_url)) # 既有root_url, 又有attr title即可
    for day_elem in day_elems:
        # assert day_elem.text.isdigit()
        new_page=page_url+day_elem.text.zfill(2)
        new_page_urls.append(new_page)
        # print('New Page:',new_page)
#
print('所有日期已收集!')
# pool=new_page_urls # 看到这pool懂我意思了吧


# 等等, 有没有可能一天有多个人发表文章的呢?
def getOneArticle(page_url):
    driver.get(page_url)
    # xp for xpath pattern
    xp_baka_cnt='//div[@class="blogTitle"]/p[@class="baka"]'
    xp_title='//div[@class="blogTitle"]/h3/a'
    xp_author='//div[@class="blogTitle"]/ul/li[@class="author"]/a'
    xp_date='//div[@class="blogTitle"]/ul/li[@class="date"]'
    xp_content='//div[@class="content"]' # 这一行有点不确定
    baka_cnt=driver.find_element_by_xpath(xp_baka_cnt).text
    # print(baka_cnt.text)
    title=driver.find_element_by_xpath(xp_title).text
    # print(title.text)
    author=driver.find_element_by_xpath(xp_author).text
    # print(author.text)
    content=driver.find_element_by_xpath(xp_content).text
    date=driver.find_element_by_xpath(xp_date).text
    # print(content.text) 这里非常完美, 本来还以为无法实现分段的, 就是一堆br和p的东西, 他帮我们封装在text里面了就很好
    filename='{}-{}-{}.txt'.format(title,author,date)
    filename=validateTitle(filename) # 小心一点, 这个很常见不应该犯了!
    words='日期:\t{}\n标题:\t{}\n作者:\t{}\n\n正文:\n{}\n\n'.format(date,title,author,content)
    with open(os.path.join(src_dir,filename),'w',encoding='utf-8') as f:
        f.write(words)
    print('{}成功保存!'.format(date))
    sleep(1) # 老实点
    # 注意, 一般这个时候会考虑一下数据库的方面, 但是这里没有考虑, 是因为暂时还没有查询的需求

# test_url='http://www.kyotoanimation.co.jp/staff/anibaka/blog/?m=20130115'
# getOneArticle(test_url)

# 单单多进程[py显然没有多线程啦!]

def validateTitle(title): # 不要忘了
    # 这个其实只是模板而已, 可以收集一下
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title

# 防止中断, 先看一看目前的文件!

alreadys=[]
for each in os.listdir(src_dir):
    already_date=each.split('-')[-1].replace('.txt','').replace('年','').replace('月','').replace('日','')
    alreadys.append(already_date)

# 单线程耗时, 每个0.371‬s



# for page in new_page_urls:
#     date=page.split('=')[1]
#     if date in alreadys: # 先回头看看
#         print('已存在!')
#         continue
#     else:
#         getOneArticle(page)
#     p=Process(target=getOneArticle,args=(page,))
#     p.start()
if __name__=='__main__': # 注意有坑! win下必须要写if name=main不知为何?
    freeze_support()
    pool=Pool(4)

    for page in new_page_urls:
        pool.apply_async(getOneArticle,args=(page,))
    pool.close()
    pool.join()
    print('用时:{}'.format(time() - start_time))





# profile.run('m1()')
# print(dates)





