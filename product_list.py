# coding:utf-8
# 对每一个子目录包含的商品明细遍历下载，如果有多页则每一页遍历下载，返回商品的url
import requests, sqlite3, os, random
from time import sleep
from lxml import html
from log import Log

cookie1 = u'skin=noskin; session-id=131-8007303-6991600; session-id-time=2082787201l; x-wl-uid=1jyw3H7W6U/BZtT76NP/k0cDO5Xpx0xrXY7El++AqydeQwpZfChVsNDW5U55BG2FZaeHRi5ZNb8Q=; ubid-main=131-0690198-1240748; session-token=uTuRoVlOk/RwqBljGnWOfZwcDWAGqiByHfbgfSE6PinxRo6ESucXePSWdWzWB/FYxbZNhMVXbJgMXk4IRsIwmwTee9idIxTI1CC4UfNl3GCEHTn5veWRdXK5e3SZexvEHw57GkrgLQ/2QJoDPneMZWhaYUXeQ7+k83AiZhY9DP+OFYJOSCkhIpI1yxfNyhtNEXP0HJ8epGWL683D02Ge6+KbPH2BLLAh15gg2RuLEAGhi+tzuQfQMVO34e+tLvCz'
cookie2 = u'skin=noskin; session-id=145-2291130-9646023; session-id-time=2082787201l; csm-hit=J3WC4145NY2BN3VWDSTW+s-J3WC4145NY2BN3VWDSTW|1494094819121; JSESSIONID=97B538F4C280DEBE1191FA3B3ADEF0B4; x-wl-uid=1/EXgRMy40luKOm2UgB2T+QXPZysexTPTcRy7jrte2I8qEaYS1OYe1SOHd6MHqXSq9avziOlOJV0=; ubid-main=132-4547050-1941243; session-token=tuKjTU47whr1IdsqhFYhj42fwMshQ5m6cSyUefWIe265z6g00VNBH0skyJdzrEItifrBUM4bF3vseAi2A1jpVEonMXTXbh+YE0Y1FLts+o+c0ohQfQ8Mj/yQrPlGz0Ftc6pnp8PRWCHKHLhGV/h9y/wOAlxprMDrwYKaUcW/GeA3uAGvlDSSLi9qa1Sqtzix44vGGqh1Dbvdu0q+3ckCVuGNMCQCwTpd7VfUyvf9dPwyyZqoGsT8n6hdo5GDVs7a'
cookie3 = u'skin=noskin; session-id=142-2600120-0453656; session-id-time=2082787201l; csm-hit=KEVXZTJ9PAD98JF49SMC+s-KEVXZTJ9PAD98JF49SMC|1494095227385; x-wl-uid=1pUW+oaW5GeA1i/w07A6TKwnJt29WtaHeAY4gKcHhdOV5NT8fGbDfFhsFuZfgHOGtrsoag7oh+ys=; ubid-main=131-5730833-8347552; session-token=BJTfbfw3qlDcGdNFx17vAyYWVmBtY9dY1BZeuBHdp9icKays6KiulqrOiZmpOsnz9VOkULadcBEPLqNWITA/R9dyoqLP/Yjn/Excq7h4S5Zf0aIz90uQ7vAgQtRxqcI/4vgPIpNvToUYsbSCAfCM/oZLWVTRkU4iFWTIWn0uCblmvFB3IC81xrmt/v6XIkWfQp05RKzmRdCqNKMqNP7U4L7yJi1i8t5ovieDAOvzaiqrOYjoqP+Jx3gE/hOI3kVY; JSESSIONID=11F46241C2AD3E492E82B9C0C75B449D'
cookie4 = u'skin=noskin; session-id=130-6064883-9558169; session-id-time=2082787201l; x-wl-uid=1gao/eEYk8Xej6EcXEYbN+Sw8ejlkMDiuK5X2x5jjvlsC6hzH1Cv4cnNPMcp4/jHtTzRJUxqdOy4=; ubid-main=130-0918625-8580058; session-token=RyfADi8WpSvcgGstjs0TJTMqMPwX7pbiKM5Rnd7j2u2BuA8zJLZ+TvZmjMVKqm9syHOuW5AWLbrHwJTrxNQ8MEKXp0F+it7erwGzd5FdvbUOJkpvACHwkg0vh+mMoP1u4ZkFYdbnm3aaRY+sIM06WVuUPLyzlx65R7NbIAvFApNpIBZXjMeqc4xyeRLR2SiCfpDDMhuVvbcwLRbNbYQ46OWvvWnQn+aDdLikqGtMLpfEgUrqihemSizKsKhykVJs'
cookie5 = u'skin=noskin; session-id=139-3925804-4399945; session-id-time=2082787201l; csm-hit=9E1SBSA9WS35AG5YRS50+s-9E1SBSA9WS35AG5YRS50|1494095861593; JSESSIONID=DA8213A4B6FC333B44FCBF654F52BE77; x-wl-uid=1icInhz7y9FDY7kIrXZlpuEXHg64J5TIzcq7KWSFXEsebw4vSizXpvlsgkW3Yr5pLms7m1pn/Bs8=; ubid-main=135-5425844-4997831; session-token=DqvC/RSpXXzFlFVBJNZi0cmAXfniYq3wC+aOArSqUc1qMvsR8xKI0bZfpD+k6Fztu4w3R6lCw1HAfvgozGHuCgS0UgvDsYC1VwPlHw8Utj6aRGcjTU0i000Vmk+SM6FLvy3gi8lybbOK8oi82+HydGbHLgJLDlfDHaXxabkm547JFPdfo7hD7UZNnDUVa8GYidHsy6GoIkmkCxtcFwux6TnXoloCaPvKQ4T4Yb8KgtFvAAjjHaEfNDKBy/vnB24W'
cookie6 = u'skin=noskin; session-id=131-5123977-3877041; session-id-time=2082787201l; x-wl-uid=1EhRK+9qx2y/2T/j4s1C0cohqMdZcSxlqf8eiiq1VK53Dl44ldVa/NnQFJ039XkVbeEOZMWNkDwc=; ubid-main=133-0128366-8457154; session-token=bKoqkJmfnod54r5qlpfS6uBJnuViKlepCgres4XK3s2G6nsUsKL/pB9trqI4F5iMLt31l1kej7I0i7th/8VkUo8IHI/Ui3StotGjGpmnYUFjK0LG4YYXQ1cR76xdSmNeRcm3I3CNHgRa7eR6LLUSN6WP3pkjYLyip8heY0FhOBJ5w10NjLW2zHy5TjrnWhoJzjV2kKEf2SkGn1rMuyDx4JP/U4TWK6nNzta9UpMjrUFUxcxbppzRSTgX+8cSgp+X'
cookie7 = u'skin=noskin; session-id=147-9157028-2618718; session-id-time=2082787201l; csm-hit=BFW1H8NQ41ESHTAPB67K+s-BFW1H8NQ41ESHTAPB67K|1494130847360; JSESSIONID=34B9DD489583C5E21F0D3EBA6D37A4E6; x-wl-uid=16YFbXf+jhvkR2uGkSLoc7CLlL2A0Mq36Tjj8M4IFnDQX1AZzLKcjuJTHbiTlLJ9GcYFGh69g4J8=; ubid-main=132-4056607-7089732; session-token=Kd8eDn0LTN9lMctb9SJEJXmR7oFymhqT2OkTBjg0+SvHDFQliasgMcc9LvSfPTx7NcQBMmuIvzZdEMSfeagQYAKNI2PszznhKyZvkIFL39OgONsJRA516ykDh+Ta7plQ9M9e4wXSnjTIROY1xJo7l52iplHP61Z+t8OBtfWpk0UN5w0j5hwZXezm6VOG2VBORVYgEoIaKAAP1gq9dpqunYqKzCY25HJ/rSV0F/uYiUOJ2mcJr8wOc8dknmvsq43x'
cookie8 = u'skin=noskin; session-id=146-6569389-3205161; session-id-time=2082787201l; csm-hit=s-8M1Y3C230GR3H60DTW8K|1494130778658; JSESSIONID=6A76DFEEC782F1A008BF26DD0F7F24CD; x-wl-uid=1wK1uNBdf8FnHrOWyD6OCzPCo6xk3ye9jWFItvYsGSnpX854pxtXGPIuQcOHm/7GqlfGDAzhr8u0=; ubid-main=132-1120054-3113563; session-token=Tpqhi5IM01zzcO6f+YyFv6NMP95L0eqcUA5cIG0cCq8VO+FND6ztHkxO2Jhu6e4HNm6ZYkbA1Cs93w0PCDkHkD7yK3LhQk96GzjE071FEpJeelL1fJlGvXPzEcvptAmlAstHKPD5L/TGD+S5grIzIZdtoiAqSqIF6bnccSmnBmMZ2olPHVEpuDVHf9P1aifzignsJwby3dK2sQEyzu+zhnPaFqMWl9a7JW/VMnIKNHXTyqY5mJxJInjzl0QnaiRG'
cookie9 = u'skin=noskin; session-id=139-1696449-7595223; session-id-time=2082787201l; csm-hit=7HTAAGH3AWJEBM9F4AZF+s-7HTAAGH3AWJEBM9F4AZF|1494130667559; x-wl-uid=1joDeWP21ee2CxNGFJzIvNNmqFbmxM9HXXfVEf2o42Bjx+lmaTkgwCs2mvhbbKC3fNvLPtPM6leA=; ubid-main=132-1383346-7098020; JSESSIONID=A5551451DC1C3F0BA8FE9563B1FC0AC8; session-token=c1bzW3BtHnutcas+kzrc1Z6QCan3/XPxu63TikSQrheUCcWQLVimFJpYUF+gMS7OM+EcsDebOlpcSlXb4Ifc38WxJhWwbX79MUASewZU3U2bbRa8WUd+srrc72TCmZw0PIXNRSbf2hUqJQbRzMr/zlFXtSfkXlhbbWvTf0r5ttL8m+vFG2S5Shwbn/P6IyzVfgs72vvXWXpcoWpYohpaPi477AVWSKbJ4zZO5OJooDFasGtIftxXXG9uA6MG6RAV'
cookie10 = u'skin=noskin; session-id=130-6829186-8999868; session-id-time=2082787201l; ubid-main=132-7685194-2850726; session-token=0+o5QDlRTeGQj3IDCI3D1Q/Aa+Cm/W7BywcPHUouabsIm/a6/6JIdnKrYLmzfZMMjYZinqOOlW2GE20rbQQwZ34ILc5MrpO4XEGfsPTHMOZkuQ3PQeuW4OgHsvfypzHEKEyEm+6Wufb044rIk14kPTdMXsxVaVtaq+ir0cCbfPeIloaRP/PncK3tONOJRMpCgD2UP/rJc/WdXQMQDHc6Mx12M93ujyOJAPBsOJYmX7IYOcniBQtTJD/DCiTrpFO4; x-wl-uid=14SGRcVeE+/PseeGJcr23UNNKAEsgOo+bjigQYp+I28H5tXyFPSAi7Cy7rb1usa4WW9cvU2xBzD8='
cookie11 = u'skin=noskin; session-id=131-2306178-5598125; session-id-time=2082787201l; csm-hit=s-SR9QBTS5GD28YHAQ6CBB|1494130059137; JSESSIONID=F184E5D099A85C0E9109FBDD24A5627F; x-wl-uid=1V+yqfOrzc5O9p+O6kdl0iOcxkZAm6MGy+KNTjRSfJYob/w0EfmS5mQd0V7NM0s3N1XkwF33Ah5k=; ubid-main=131-6788858-8514648; session-token=6vzEH+1vVKnKG/duHiYhauc0cVyOQAQi40wjaFGM620MrOPzpQ0x2kAPWEfFyzwOCcpq2aBmLx0InJ1xaOkCDnOiLDZX781O5xlRp5mzK+Wyf5RSR+tSyGRbQpQK1wj64N4pUDBIWoThD6SefVARdpOHIQwr3aab5xk9R7pJQrg72wwyxwjMsacmbgQmDzdY/BtPBxFiik2CMnz0fKH7ODWp5q1Bsb/+JOVtMKk/NgvqCHkGOUlKvXlfcB70l2Iw'
cookie12 = u'skin=noskin; session-id=139-0555439-1135044; session-id-time=2082787201l; ubid-main=130-7824371-8227328; JSESSIONID=DFC11B5AC577F38EF753FF1BC6838C36; x-wl-uid=1O5uOUyn1t/iqaVFI+ejjvFvnxfV3efohQ7FY59yqwuU16KW7jEcCLn8NziqpenJr/hIvHkRy3zQ=; session-token=03t/djkbwHxNWXdvX9mVB6NxCKrkPyu/QUO7GCJLor22oSJPife8yJOgVggk+J1krceoH6MDTy1q4ZM/ERVcqzquVZnEgn9aoWkDXglG2m7gOv/883qmRgC1zkU2TPZCYTRTV/l9bh/0WcQboGIfcbMUiC6BVBvGOdKIW4KSvde8Sokh338FblhnxdydZcau8VsP7TT+oInaO2zJVehfsOYgGQnhrPY/cSEKPUyNlRSPNOLD+sLvL0NXkFlUo4WS; csm-hit=GX5D0YKBMBSZJMJ0Z9BC+s-GX5D0YKBMBSZJMJ0Z9BC|1494132231810'
cookie13 = u'skin=noskin; session-id=146-2270052-3256036; session-id-time=2082787201l; csm-hit=FMSCJX98SDQQQZ1V07FA+s-FMSCJX98SDQQQZ1V07FA|1494132529029; JSESSIONID=A13E6D95AF4D514F37321D139EC6D21F; x-wl-uid=1szHHNpYJAZb2W4iuNTvP9u142RfYeatWPzL3OTs5Ux9xsLA+r7nx5gFyXmWTBE/v466vBUMpADM=; ubid-main=130-1255486-1291757; session-token=mYUl77/gao/GkJy4BCUspM0Zu6B9DwRUy5BaGF00WUS5Ix2seLyy5XR6yBOjsFqP4Syc/c1OmZnwtLFidb9OxzNAMFqd9B/yXKHwTXiZJquCTetj0xEV5qy6CBQTheWAzHKHSBqAKCli3qJCZm7UaBWEm4gy05KgdGRmURWpjCe/v+OCBVm0BypnRDxApk4gQuHYQXBKM0u/Ny2vkZr//Hp8DwKQavsF/6C4OE3yHuhqlo/NwjqLKnpZDf5bG7tL'
cookie14 = u'skin=noskin; session-id=138-2565905-6614804; session-id-time=2082787201l; csm-hit=BJF3HHQZ5HFF3X0QX2SH+s-BJF3HHQZ5HFF3X0QX2SH|1494133695772; JSESSIONID=50A782AAE97FC624D03F2CBC35ABA62E; x-wl-uid=1mJ0rTWxFEX/FSWPUVBC8Br6Hi0Y7nh+pgVDAj/uYErMepKw1DYR4G0pdEIPxPrgB6XY8N1VSlik=; ubid-main=132-5926404-4962703; session-token=FMWStKOyaPGXgyy2TgiMtKclfw+aMEfnw+iU3eWv+lGD3XW278kEyc/LnnLMpJIyA6UE1v0c/QAYzyCk3Mdb6R7j8Nbl+HunVmnTXUMU8JPwxhmc55vMgpX1ThR1p2av2h/0GDvHZjQ3cKsikl0W1+/1gatqh6Vo9ApZuQwemMJZv59HrrzYgo93zYU0ygncDLAfd+ztr5f4B7RAU7moKOnvwHcWReTyJaM1EPwhfnzIGwedNKdYaBcAA0zZDh4t'

proxies = { "https": "https://52.34.132.230:3128",}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'X-Forwarded-For': '::ffff:' + str(random.randint(11, 170)) + u'.' + str(random.randint(1, 254)) + u'.' + str(random.randint(1,254)) + u'.' + str(random.randint(1, 254)),
    'X-Forwarded-Protocol': '',
    'Cookie': u'cookie' + str(random.randint(1, 14)),
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
        insert_error(product_url, e)
        pass


def insert_error(product_url, reason):
    conn = sqlite3.connect(db_path)
    sql_insert = '''
    INSERT INTO
        'error' (error_url, reason)
    VALUES
        (?, ?);
    '''
    try:
        conn.execute(sql_insert, (product_url, reason))
        conn.commit()
        conn.close()
    except Exception as e:
        Log.log('insert:', e)
        Log.log('insert errors:')
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
    path = os.path.join(dictionary_name, category_path + u'_' + str(page_number) + u'.html')
    if os.path.exists(path):  # amazon会进行反爬虫，所以第二次爬的时候对已经爬过的做判断。
        pass
    else:
        page = cached_url(dictionary_name, url, category_path, page_number)
        while os.path.getsize(os.path.join(dictionary_name, category_path + u'_' + str(page_number) + u'.html')) < 10000:
            Log.log(u'html<10K:', url)
            insert_error(url, str('html<10k'))
            os.remove(os.path.join(dictionary_name, category_path + u'_' + str(page_number) + u'.html'))
            sleep(600)
            page = cached_url(dictionary_name, url, category_path, page_number)  # 爬回的页面小于10k是Amazon反爬虫页面，sleep10分钟小时后删掉重新下载页面
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
                    Log.log('log1:', len(page_current))
                    Log.log('log1 conditons:', url, category_path, page_number)
            page_next_url = root_url + page_next_url[0]  # 转换为完整的url格式http://www.amazon.com/dfdfdfdsf/dfldfj
        else:
            for p in page_list_div:
                try:
                    page_content = p.xpath('./@*')
                    # print(page_content[1], page_content[2])  # product对应的名称和url
                    insert_product_list(page_content[1], page_content[2], None, int(page_current[0].text), category_path)
                except Exception as e:
                    Log.log('log2:', len(page_current))
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
            except Exception as E:
                Log.log('main:', E)
                Log.log('log:', page_next_url, end_of_category_url[e][1], page_number)
                pass
                # sleep(random.randint(2, 11))


if __name__ == '__main__':
    main()
