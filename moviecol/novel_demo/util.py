from requests.adapters import HTTPAdapter
import requests


def gethtml(url):
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=5))  # 设置重试次数为3次
    s.mount('https://', HTTPAdapter(max_retries=5))

    hea = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
    i = 0
    while i < 5:
        try:
            html = s.get(url, timeout=8, headers=hea)
            return html
        except requests.exceptions.ConnectionError as e:
            print('连接超时，重新连接')


def get_left(nowIndex):
    nowIndex = int(nowIndex)
    if nowIndex < 10:
        left_num = str('000' + str(nowIndex))
    elif nowIndex < 100:
        left_num = str('00' + str(nowIndex))
    elif nowIndex < 1000:
        left_num = str('0' + str(nowIndex))
    else:
        left_num = str(nowIndex)
    return left_num


def get_right(chapter_num):
    chapter_num = int(chapter_num)
    if int(chapter_num) < 10:
        right_num = str('000' + str(chapter_num))
    elif int(chapter_num) < 100:
        right_num = str('00' + str(chapter_num))
    elif int(chapter_num) < 1000:
        right_num = str('0' + str(chapter_num))
    else:
        right_num = str(chapter_num)
    return right_num
