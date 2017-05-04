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
    'Cookie': 'skin=noskin; session-id=134-3650392-7691709; session-id-time=2082787201l; JSESSIONID=3D2AD46C7EEA6A6BCB853A63D801CD75; x-wl-uid=1cts8UGMpr//UZfgZrmYJpz8swxXoWqpICEPP0xHG8WQxfHLUfgv8TwM5nDHHfF+RpaZKt2wYRzk=; ubid-main=130-5987508-3520124; csm-hit=5M3P8SZ5APMV5PYVKYP2+s-8G9CVHES6M6X2V1BME14|1493728207733; session-token=ea+beZYzGxaZtekrmW1BH8nf0mi6pSahTEijxRrKgFPA3AbrL0WAEeMbok+D8nsKjbEoU3EbzQTVpxu2aZr9ETOiLp29yZxVEugTg+SaF2Z/x3JF5fKQ4bc1ZjqQVm5AelXfGGA0ZSkZraJuk4+QpUrGb8vep96B4fcv+b8L9oEDLxAAZLfvlSVCFMp+Se5Bzsd1n05K8N/ABvKtjW3YbxqUuvS0naOpiJzR5AhJCi/+ifiXU2ZLz/enE2YeRr4x',
    'DNT': '1',
    'Proxy-Authorization': 'Basic cm9vdDpwYWMuaXR6bXguY29t',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0, no-cache',
    'Pragma': 'no-cache',
}

db_path = os.path.join(os.getcwd(), 'Amazon.db')
root_url = u'http://www.amazon.com'


def select(option):
    conn = sqlite3.connect(db_path)
    if option == 'select1':
        sql = '''
        SELECT
            category_url, category_path
        FROM
            category
        WHERE
            end_of_category=1
        '''
        cursor = conn.execute(sql)
        all_result = cursor.fetchall()
        conn.commit()
        conn.close()
        return all_result


def insert_product_list(product_name, product_url, page_sum_number, page_current_number, category_path):
    conn = sqlite3.connect(db_path)
    sql_insert = '''
    INSERT INTO
        `product_list` (product_name, product_url, product_sum_numbers, product_current_page_number, category_path)
    VALUES
        (?, ?, ?, ?, ?);
    '''
    try:
        conn.execute(sql_insert, (product_name, product_url, page_sum_number, page_current_number, category_path))
        conn.commit()
        conn.close()
    except Exception as e:
        Log.log('insert:', e)
        Log.log('insert:', product_name, product_url, page_sum_number, page_current_number, category_path)
        pass


def cached_url(dictionary_name, url, category_path, page_number):  # 把网页下载下来，目录和明细分开存放，依据dictionary_name的值判断
    path = os.path.join(dictionary_name, category_path + u'_' + str(page_number) + u'.html')
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return f.read()
    else:
        r = requests.get(url, headers=headers)
        with open(path, 'wb') as f:
            f.write(r.content)
    return r.content


def page_from_url(dictionary_name, url, category_path, page_number):
    page = cached_url(dictionary_name, url, category_path, page_number)
    root = html.fromstring(page)
    page_list_div = root.xpath(
        '//a[@class="a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal"]')
    page_current = root.xpath('//span[@class="pagnCur"]')
    # page_total = root.xpath('//span[@class="pagnDisabled"]')  # 有的页面没有总页数这个字段，先不采用这个字段先
    page_next_url = root.xpath('//a[@id="pagnNextLink"]/@href')
    # print(page_current[0].text, page_total[0].text, page_next_url[0])
    if page_next_url:  # 最末尾页没有next_url
        for p in page_list_div:
            try:
                page_content = p.xpath('./@*')
                insert_product_list(page_content[1], page_content[2], None, int(page_current[0].text), category_path)
            except Exception as e:
                Log.log('log1:', len(page_content), len(page_current))
                Log.log('log1 conditons:', url, category_path, page_number)
        page_next_url = root_url + page_next_url[0]  # 转换为完整的url格式http://www.amazon.com/dfdfdfdsf/dfldfj
    else:
        for p in page_list_div:
            try:
                page_content = p.xpath('./@*')
                # print(page_content[1], page_content[2])  # product对应的名称和url
                insert_product_list(page_content[1], page_content[2], None, int(page_current[0].text), category_path)
            except Exception as e:
                Log.log('log2:', len(page_content), len(page_current))
                Log.log('log2 conditionurl', url, category_path, page_number)
                pass
        page_next_url = ''
    return page_next_url


def main():
    end_of_category_url = select('select1')  # 每一个end_path的url和category_path
    for e in range(0, len(end_of_category_url)):
        # print(e, root_url + end_of_category_url[e][0], end_of_category_url[e][1])
        page_number = 1
        page_next_url = page_from_url('product_page_list', root_url + end_of_category_url[e][0],
                                      end_of_category_url[e][1], page_number)
        while page_next_url:
            page_number = page_number + 1
            try:
                page_next_url = page_from_url('product_page_list', page_next_url,
                                              end_of_category_url[e][1], page_number)
            except Exception as e:
                Log.log('main:', e)
                Log.log('log:', page_next_url, end_of_category_url[e][1], page_number)
                pass
            # sleep(random.randint(1, 5))


if __name__ == '__main__':
    main()
