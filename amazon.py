# coding:utf-8
# 把Software目录下的各个子目录明细遍历下载，返回每一个子目录的目录明细，只有最末尾那一层才是包含商品页的url
import requests, sqlite3, os, random
from time import sleep
from lxml import html
from log import Log

headers = {
    # 'Host': 'www.amazon.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cookie': 'skin=noskin; session-id=144-9847520-9027834; session-id-time=2082787201l; x-wl-uid=1RjuleI2xjMq0dWRl6CCow1JLaC2EXuonYCnkAf4q+j3tFXvMSeFzMa/hMONbTTguun/jlr9XHJc=; ubid-main=132-4989230-0589508; session-token=PQ3k+BLfco266m0mIVArSqM+nrsRM1b6QlkCX79KGgC5uA6aSwXA51BGGmWuNw0Y684OnoPOZ3K57fQGtU+eJkHA1dhEksPK1A0YD/3+Vg0cZaBir/IRHtM+zkjJRzsDqSx6sHRIAr6EMC/wT4qunbn3UuUNXy9z0N+cVqz48DufDiO8i5HTU2dgDwB/BgAbwmEu6+bptvFcxM+mBjd2/2yaJuNau/lnptQxGi5MkqmF3mklbPz0fTfOJbCIHTNe; JSESSIONID=2EC31C82858201F1C2166879EAD0F665; csm-hit=PB29NK3G96VF859JZBBM+s-PB29NK3G96VF859JZBBM|1493474890903',
    'DNT': '1',
    'Proxy-Authorization': 'Basic cm9vdDpwYWMuaXR6bXguY29t',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0, no-cache',
    'Pragma': 'no-cache',
}

db_path = os.path.join(os.getcwd(), 'Amazon.db')


def insert_category(category_name, category_path, category_url, end_of_category, previous_level_category, access):
    conn = sqlite3.connect(db_path)
    sql_insert = '''
    INSERT INTO
        `category` ('category_name', 'category_path', 'category_url',
                    'end_of_category', 'previous_level_category', 'access')
    VALUES
        (?, ?, ?, ?, ?, ?);
    '''
    try:
        conn.execute(sql_insert, (category_name, category_path, category_url[0], end_of_category, previous_level_category, access))
        conn.commit()
        conn.close()
    except:
        Log.log('insert:',category_name, category_path, category_url[0], end_of_category, previous_level_category, access)
        pass


def select(option):
    conn = sqlite3.connect(db_path)
    if option == 'select1':
        sql = '''
        SELECT
            count(*)
        FROM
            category
        WHERE
            end_of_category=0 and access=0
        '''
        cursor = conn.execute(sql)
        all_result = cursor.fetchall()
    elif option == 'select2':
        sql = '''
        SELECT
            category_path, category_url
        FROM
            category
        WHERE
            end_of_category=0 and access=0
        '''
        cursor = conn.execute(sql)
        all_result = cursor.fetchall()
        conn.commit()
        conn.close()
    return all_result


def update(end_of_category, access, previous_level_category):
    conn = sqlite3.connect(db_path)
    sql_update = '''
    UPDATE
        `category`
    SET
        `end_of_category`=?, 'access'=?
    WHERE
        `category_path`=?
    '''
    Log.log('update:', previous_level_category)
    conn.execute(sql_update, (end_of_category, access, previous_level_category))
    conn.commit()
    conn.close()


def cached_url(dictionary_name, url, category_path):  # 把网页下载下来，目录和明细分开存放，依据dictionary_name的值判断
    path = os.path.join(dictionary_name, category_path+u'.html')
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return f.read()
    else:
        r = requests.get(url, headers=headers)
        with open(path, 'wb') as f:
            f.write(r.content)
    return r.content


def category_from_url(dictionary_name, url, category_path):
    page = cached_url(dictionary_name, url, category_path)
    root = html.fromstring(page)
    category_div = root.xpath('//div[@class="categoryRefinementsSection"]/ul/li')
    judge_the_end_category = category_div[-1].xpath('.//a/@href')
    for c in reversed(category_div):
        # print(c[0].text, len(c))
        if len(judge_the_end_category) == 0:  # 终点链接点最底层没有链接点
            update(1, 1, category_path)
            break
        category_url = c.xpath('.//a/@href')  # 非终点链接点附有链接，如果碰到没有链接属性表示它上级节点
        if category_url:
            # Log.log(type(c.xpath('.//span[@class="refinementLink"]')), len(c.xpath('.//span[@class="refinementLink"]')))
            category_name = c.xpath('.//a/span[@class="refinementLink"]')[0].text
            category_path_new = category_path + u'_' + category_name
            category_url = category_url
            end_of_category = 0
            previous_level_category = category_path
            access = 0
            insert_category(category_name, category_path_new, category_url,
                            end_of_category, previous_level_category, access)
        else:
            update(0, 1, previous_level_category)
            break

def main():
    # url = u'http://www.amazon.com/design-download-business-education-software/b/ref=nav_shopall_sw?ie=UTF8&node=229534'
    # category_from_url(u'category', url, u'Root_Software')
    count_category = select('select1')[0][0]  # 未遍历的数量
    while count_category:
        params = select('select2')
        for p in range(0, len(params)):
            url = u'http://www.amazon.com'+ params[p][1]
            # Log.log(url, params[p][0])
            category_from_url(u'category', url, params[p][0])
            sleep(random.randint(2, 5))
        count_category = select('select1')[0][0]
    # # while count_category:


if __name__ == '__main__':
    main()