from bs4 import BeautifulSoup
import pymysql
import math


###
###  获取小说信息，增量爬取
###

# 获取小说信息
from util import gethtml


def get_novel(page, conn):

    # 查询数据库已保存的小说id
    sql = 'select novel_id from t_novel'
    cursor = conn.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    cursor.close()
    saved_ids = []
    for i in range(len(rs)):
        saved_ids.append(str(rs[i][0]))
    print(saved_ids)
    # 开始爬取
    print("开始爬取第", str(page), "页")
    data = []
    url = "https://boxnovel.com/novel/page/"+str(page)+"/?m_orderby=alphabet"
    html = gethtml(url)
    soup = BeautifulSoup(html.text, "lxml")
    item = soup.select('div[class="page-item-detail"] > div > a')
    novel_ids = soup.select('div[class="page-item-detail"] >:first-child ')
    for i in range(len(item)):
        # 判断小说是已经存在
        if novel_ids[i].get('data-post-id') in saved_ids:
            print("第", str((page - 1) * 10 + (i+1)), "本小说已存在----跳过")
            continue
        url = item[i].get('href')
        print("正在爬取第" + str((page - 1) * 10 + (i+1)) + "篇小说:" + url)
        html = gethtml(url)
        soup = BeautifulSoup(html.text, "lxml")
        # 小说名
        novel_name = soup.select('div[class="post-title"] > h3')[0].text.replace('HOT',"").replace('NEW','').strip()
        # 小说ID
        novel_id = novel_ids[i].get('data-post-id')
        # 别名
        alternative = soup.select('div[class="summary-content"]')[1].text.strip()
        # 作者
        author_name = soup.select('div[class="author-content"] > a')
        name_id = 0
        name = 'Updating'
        # 查询作者总数
        sql = 'select count(id) from t_author'
        cursor = conn.cursor()
        cursor.execute(sql)
        rs = cursor.fetchall()
        author_count = rs[0][0]
        print("当前作者总数：",author_count)
        if len(author_name) > 0:
            # 查询作者是否存在
            name = author_name[0].text
            sql = 'select author_name from t_author'
            cursor = conn.cursor()
            cursor.execute(sql)
            rs = cursor.fetchall()
            cursor.close()
            author_list = []
            for r in rs:
                author_list.append(r[0])
            #  如果作者存在，从数据库取
            if str(name) in author_list:
                select_sql = "select author_id from t_author where author_name = '%s'" % str(name)
                cursor = conn.cursor()
                cursor.execute(select_sql)
                rs = cursor.fetchall()
                cursor.close()
                name_id = rs[0][0]
            #  如果作者不存在，添加到数据库
            else:
                name_id = author_count + 1
                sql = 'insert into t_author(`author_id`,`author_name`,`status`,`create_at`,`update_at`,`enable`) values (%s,%s,%s,%s,%s,%s);'
                author_info = []
                author_info.append((str(name_id),str(name),str(0),str(1575023154),str(1575023154),str(1)))
                cursor = conn.cursor()
                cursor.executemany(sql,author_info)
                print("添加作者成功")
        # 摘要
        summary = soup.select('div[class="description-summary"] > div')[0]
        # 类别
        genres = soup.select('div[class="genres-content"] > a')
        genres_id = []
        for genre in genres:
            genres_id.append(str(getGenres(genre.text)))
        # 类型
        type = soup.select('div[class="summary-content"]')[5].text.strip()
        type = getType(type)
        # 图片
        image_url = soup.select('div[class="summary_image"] img')[0].get('src')
        # 发布时间
        release = soup.select('div[class="summary-content"] > a')
        if len(release) > 0:
            release = release[0].text.strip()
        else:
            release = 'Updating'
        # 状态
        status = soup.select('div[class="summary-content"]')[3].text.strip()
        if status == 'Updating':
            status = 1
        else:
            status = 2
        data.append((str(novel_id),str(novel_name), str(alternative)[0:255], str(name_id),str(name),
            str(summary), str(",".join(genres_id)), str(type), str(html.url), str(image_url), str(release), str(status),str('1575023154'),str('1575023154'),str(1)))
        print("爬取第"+str((page - 1) * 10 + (i+1))+"篇成功")
        print(data)
        print(len(data))
    return data


def getType(str):
    if str == 'Chinese Web Novel':
        return 1
    elif str == 'Japanese Web Novel':
        return 2
    elif str == 'Korean Web Novel':
        return 3
    else:
        return 4

def getGenres(str):
    if str == 'Action':
        return 1
    elif str == 'Adventure':
        return 2
    elif str == 'Comedy':
        return 3
    elif str == 'Fantasy':
        return 4
    elif str == 'Romance':
        return 5
    elif str == 'Harem':
        return 6
    elif str == 'Martial Arts':
        return 7
    elif str == 'Ecchi':
        return 8
    elif str == 'Shounen':
        return 9
    elif str == 'School Life':
        return 10
    elif str == 'Drama':
        return 11
    elif str == 'Horror':
        return 12
    elif str == 'Shoujo':
        return 13
    elif str == 'Josei':
        return 14
    elif str == 'Mature':
        return 15
    elif str == 'Mystery':
        return 16
    elif str == 'Sci-fi':
        return 17
    elif str == 'Seinen':
        return 18
    elif str == 'Slice of Life':
        return 19
    elif str == 'Tragedy':
        return 20
    elif str == 'Supernatural':
        return 21
    elif str == 'Psychological':
        return 22
    else:
        return 0


def start_novel():
    conn = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="fyj1999",
        database="novel",
        charset="utf8mb4"
    )
    sql = "insert into t_novel(`novel_id`,`novel_name`,`alternative`,`author_id`,`author_name`,`summary`,`genres`,`type_id`,`origin_url`,`image_url`,`release`,`status`,`create_at`,`update_at`,`enable`) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
    print("数据库连接成功")

    html = gethtml("https://boxnovel.com/novel")
    soup = BeautifulSoup(html.text, "lxml")
    count = ''.join(c for c in soup.select('div[class="tab-wrap"]  h4')[0].text.strip() if c.isdigit())
    print("novel box--总小说数：",count)
    page = math.ceil(int(count)/10)

    for i in range(1,page+1):
        result = get_novel(i,conn)
        cursor = conn.cursor()
        cursor.executemany(sql, result)
        conn.commit()
        print("提交")

    # 关闭连接
    conn.close()



