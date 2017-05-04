import requests, sqlite3, os
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


def insert_product_details( title, star, asin, best_seller_ranker, price, product_url):
    conn = sqlite3.connect(db_path)
    sql_insert = '''
    INSERT INTO
        `product_details` ('brand', 'title', 'star', 'reviews', 'answers_quwstions_url',
                    'asin', 'best_seller_ranker', 'price', 'product_url')
    VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?);
    '''
    # 参数拼接要用 ?，execute 中的参数传递必须
    # 是一个 tuple 类型
    # print(type(category_name), type(category_path), type(category_url), type(end_of_category), type(previous_level_category), type(access))
    try:
        conn.execute(sql_insert,
                     (brand, title, star, reviews, answers_questions_url, asin, best_seller_ranker, price, product_url))
        conn.commit()
        conn.close()
    except Exception as e:
        Log.log('insert:', e)
        Log.log('insert:', product_url)
        pass


def insert_product_details2( title, star, asin, best_seller_ranker, price, product_url):
    conn = sqlite3.connect(db_path)
    sql_insert = '''
    INSERT INTO
        `product_details` ('title', 'star', 'asin', 'best_seller_ranker', 'price', 'product_url')
    VALUES
        (?, ?, ?, ?, ?, ?);
    '''
    # 参数拼接要用 ?，execute 中的参数传递必须
    # 是一个 tuple 类型
    # print(type(category_name), type(category_path), type(category_url), type(end_of_category), type(previous_level_category), type(access))
    try:
        conn.execute(sql_insert,
                     (title, star, asin, best_seller_ranker, price, product_url))
        conn.commit()
        conn.close()
    except Exception as e:
        Log.log('insert:', e)
        Log.log('insert:', product_url)
        pass


def select(option):
    conn = sqlite3.connect(db_path)
    if option == 'select1':
        sql = '''
        SELECT
            product_url, category_path, product_name
        FROM
            product_list
        '''
        cursor = conn.execute(sql)
        all_result = cursor.fetchall()
        return all_result


def cached_url(dictionary_name, url, category_path, product_name):  # 把网页下载下来，目录和明细分开存放，依据dictionary_name的值判断
    path = os.path.join(dictionary_name, category_path + product_name + u'.html')
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return f.read()
    else:
        r = requests.get(url, headers=headers)
        with open(path, 'wb') as f:
            f.write(r.content)
    return r.content


def detail_from_url(dictionary_name, url, category_path, product_name):
    try:
        # page = cached_url(dictionary_name, url, category_path, product_name)
        page = requests.get(url).content
        root = html.fromstring(page)
        brand = root.xpath('//a[@id="brand"]')
        title = product_name
        star = root.xpath('//div[@id="centerCol"]/descendant::span[contains(., "out of 5 stars")]')
        reviews = root.xpath('//span[@id="acrCustomerReviewText"]')
        answers_questions_url = root.xpath('//div[@class="cdQuestionLazySeeAll"]/a/@href')  # answers_questions[0]
        asin = root.xpath('//form[@id="addToCart"]/input[@id="ASIN"]/@value')
        best_seller_rank = root.xpath('//table[@id="productDetailsTable"]/descendant::li[@id="SalesRank"]/text()')
        price = root.xpath('//div[@id="centerCol"]/descendant::span//text()[contains(., "$")]')
        if len(brand):
            if brand[0].text:
                brand = brand[0].text.strip()  # 去掉前后空格
            else:
                brand = root.xpath('//a[@id="brand"]/@href')[0]
        star = star[-1].text
        if len(reviews):
            reviews = reviews[0].text.split(' ', 1)[0]  # 429 reviews 的格式
        else:
            reviews = None
        if len(answers_questions_url):
            answers_questions_url = answers_questions_url[0]
        else:
            answers_questions_url = None
        asin = asin[0]
        if best_seller_rank:
            best_seller_rank = best_seller_rank[1].split('#', 1)[1].split(' ', 1)[0]  # 按格式：  #4 in Software ( 提取有效排位数
        else:
            best_seller_rank = None
        if len(price) >= 2:  # 如果返回有多个价格，取第二个价格，否则取第一个或者None
            price = price[1].strip()
        elif price:
            price = price[0].strip()
        else:
            price = None
        # insert_product_details2(title, star, asin, best_seller_rank, price, url)
    except Exception as e:
        Log.log('detail', e)
        Log.log('details', url)
        pass


def main():
    product_information = select('select1')
    for p in product_information:
        product_url, category_path, product_name = p
        # print(product_url, category_path+product_name)
        try:
            detail_from_url('product_detail', product_url, category_path, product_name)
        except Exception as e:
            Log.log('main:', e)
            Log.log('main_detail:', product_url)
            pass


if __name__ == '__main__':
    main()
