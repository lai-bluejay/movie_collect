from bs4 import BeautifulSoup
import pymysql
import math
import os
import time
import boto3
from util import gethtml, get_left, get_right


###
###  获取小说章节，增量爬取
###

def start_chapter():
    print("连接数据库")
    conn = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="fyj1999",
        database="novel",
        charset="utf8mb4"
    )

    print("连接S3服务器")
    s3 = boto3.resource('s3')

    save_count = 0

    # 获取小说总数
    sql = 'select count(`id`) from t_novel'
    cursor = conn.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    conn.commit()
    count = rs[0][0]

    # 分页查询爬取小说章节
    for i in range(0, math.ceil(count / 20)):
        nowIndex = i*20+1
        # 章节数据 t_novel_chapter
        chapter_data = []
        print('第' + str(i + 1) + '页')
        # 分页查询 SQL
        page_sql = 'select novel_id,origin_url from t_novel limit %d,20' % (i * 20)
        # 保存章节数据 SQL
        save_sql = "insert into t_novel_chapter(`chapter_id`,`novel_id`,`title`,`num`,`sub_num`,`origin_url`,`content_url`,`status`,`create_at`,`update_at`,`enable`) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        cursor.execute(page_sql)
        rs = cursor.fetchall()
        conn.commit()
        for novel in rs:
            # 小说info信息是否存在
            isNew = False
            # 小说是否只有一章
            isOne = False
            # 小说信息 t_novel_info
            novel_info_data = []
            print("第"+str(nowIndex)+"本小说")
            folder = novel[1].split("/")[-2]
            html = gethtml(novel[1])
            novel_id = novel[0]
            soup = BeautifulSoup(html.text, "lxml")
            print(html.url)
            # 章节列表
            chapter_list = soup.select('li[class="wp-manga-chapter"] > a')
            # 查询数据库中小说章节数
            select_sql = "select chapter_amount from t_novel_info where novel_id = '%s'" % str(novel_id)
            cursor.execute(select_sql)
            amount = cursor.fetchall()
            conn.commit()
            if len(amount) == 0:
                isNew = True
            else:
                if int(amount[0][0]) >= len(chapter_list):
                    print("第"+str(nowIndex)+"本小说已是最新-----跳过")
                    nowIndex += 1
                    continue
            if len(chapter_list) == 0:
                nowIndex += 1
                continue
            # 判断是否只有一章
            if len(chapter_list) == 1:
                last_chapter = str(get_left(nowIndex) + str(get_right(1)))
                last_last_chapter = "0"
                isOne = True
            else:
                # 最后一章
                try:
                    last_chapter = ''.join(c for c in chapter_list[0].text.strip().split(" ")[1].replace(".", "0").replace(":", "") if c.isdigit())
                    if len(last_chapter.strip()) == 0:
                        last_chapter = ''.join(c for c in chapter_list[0].text.strip().split("\xa0")[1].replace(".", "0").replace(":", "").split(" ")[0] if c.isdigit())
                except IndexError:
                    last_chapter = chapter_list[0].get('href').split('/')[-1].split('-')[1]
                last_chapter = str(get_left(nowIndex) + str(get_right(last_chapter)))
                # 最后一章前一章
                try:
                    last_last_chapter = ''.join(c for c in chapter_list[1].text.strip().split(" ")[1].replace(".", "0").replace(":", "").replace("_","") if c.isdigit())
                    if len(last_last_chapter.strip()) == 0:
                        last_last_chapter = ''.join(c for c in chapter_list[1].text.strip().split("\xa0")[1].replace(".", "0").replace(":", "").replace("_","").split(" ")[0] if c.isdigit())
                except IndexError:
                    last_last_chapter = chapter_list[1].get('href').split('/')[-1].split('-')[1]
                last_last_chapter = str(get_left(nowIndex) + str(get_right(last_last_chapter)))
            if isNew:
                novel_info_sql = "insert into t_novel_info(`novel_id`,`last_chapter_id`,`last_last_chapter_id`,`chapter_amount`,`view_times`) values (%s,%s,%s,%s,%s)"
                novel_info_data.append(
                    (str(novel_id), str(last_chapter), str(last_last_chapter), str(len(chapter_list)), str(0)))
            else:
                novel_info_sql = "update t_novel_info set last_chapter_id= %s,last_last_chapter_id= %s,chapter_amount= %s where novel_id = %s"
                novel_info_data.append(
                    (str(last_chapter), str(last_last_chapter),str(len(chapter_list)) ,str(novel_id)))
            for chapter in chapter_list:
                chapter_origin = chapter.get('href')
                file_name = chapter_origin.split("/")[-1]
                # 判断数据库中是否存在此章节
                select_sql = "select count(id) from t_novel_chapter where origin_url = '%s'" % str(chapter_origin)
                cursor.execute(select_sql)
                count = cursor.fetchall()[0][0]
                if count > 0:
                    print("章节已存在----跳过")
                    continue
                print(chapter.text.strip())
                print(chapter.get('href'))
                if isOne:
                    chapter_num = 1
                    sub_num = None
                else:
                    try:
                        chapter_num = chapter.text.strip().split(" ")[1].replace(":","").replace("_","")
                        if len(chapter_num.strip()) == 0:
                            chapter_num = chapter.text.strip().split("\xa0")[1].replace(":","").replace("_","")
                    except IndexError:
                        chapter_num = file_name.split("-")[1].replace("_", "")
                    if "." in chapter_num:
                        chapter_num = ''.join(c for c in chapter_num.split(".")[0] if c.isdigit())
                        sub_num = ''.join(c for c in chapter_num.split(".")[1] if c.isdigit())
                    elif "-" in chapter_num:
                        chapter_num = ''.join(c for c in chapter_num.split("-")[0] if c.isdigit())
                        sub_num = ''.join(c for c in chapter_num.split("-")[1] if c.isdigit())
                    else:
                        chapter_num = ''.join(c for c in chapter_num if c.isdigit())
                        sub_num = None

                print("num:"+chapter_num+",sub_num:"+str(sub_num))
                chapter_html = gethtml(chapter.get('href'))
                chapter_soup = BeautifulSoup(chapter_html.text, "lxml")
                chapter_text = chapter_soup.select('div[class="text-left"]')
                title = chapter.text.strip()
                if not os.path.exists("chapter/" + folder):
                    os.mkdir("chapter/" + folder)
                fo = open("chapter/" + folder + "/" + file_name + ".txt", "w", encoding='utf-8')
                fo.write(str(chapter_text[0]))
                fo.close()
                print("存储服务器")
                data = open("chapter/" + folder + "/" + file_name + ".txt", "rb")
                s3.Bucket('novel-txt').put_object(Key="novel/"+folder+"/"+file_name+".txt", Body=data)

                if len(chapter_list) == 1:
                    left_num = get_left(nowIndex)
                    right_num = str('0001')
                    chapter_num = 1
                else:
                    left_num = get_left(nowIndex)
                    if sub_num is None:
                        right_num = get_right(chapter_num)
                    else:
                        right_num = '%s0%s' % (get_right(chapter_num), str(sub_num))

                chapter_data.append(
                    ('%s%s' % (left_num, right_num),
                     str(novel_id),
                     str(title),
                     str(chapter_num),
                     sub_num,
                     str(chapter_origin),
                     str("/novel/"+folder + "/" + file_name+".txt"),
                     0,
                     str(int(time.time())),
                     str(int(time.time())),
                     1
                     )
                )
                save_count += 1
                print(chapter_data)
                print(novel_info_data)
                if save_count % 10 ==0:
                    cursor.executemany(save_sql, chapter_data)
                    conn.commit()
                    save_count = 0
                    chapter_data = []
                    print("保存")
            if len(chapter_data) > 0:
                cursor.executemany(save_sql, chapter_data)
                conn.commit()
                save_count = 0
                chapter_data = []
                print("保存")
            print(novel_info_sql)
            cursor.executemany(novel_info_sql, novel_info_data)
            conn.commit()
            nowIndex += 1
