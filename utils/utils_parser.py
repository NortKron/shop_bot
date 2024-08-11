#import base64
import json
import os
import time
import random
import requests
import logging

from bs4 import BeautifulSoup
from decimal import Decimal
from datetime import datetime
from urllib.parse import urljoin

#from db.models import Category
from shop_parser.models_old import Category

from shop_parser.crud import bulk_insert_products, get_or_create_category
#from shop_parser.engine import create_db

dictionaty_urls = {
    'shop.kz' : 'https://shop.kz',
    'arbuz.kz' : 'https://arbuz.kz'
}

def reload_request(session, method, url, data=None, params=None):
    try:
        methods = {'GET': session.get, 'POST': session.post}
        response = methods[method](url, data=data, params=params)
        response.raise_for_status()

        delay = random.uniform(1, 3)
        time.sleep(delay)
        
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
        time.sleep(random.uniform(1, 3))
        return None
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")
        time.sleep(random.uniform(1, 3))
        return None


def read_html_file(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
        return html_content


def write_to_file(file_name, data):
    if not os.path.exists(file_name):
        with open(file_name, 'w') as file:
            json.dump([], file)
    with open(file_name, 'r') as file:
        existing_data = json.load(file)
    existing_data.append(data)
    with open(file_name, 'w') as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)


def convert_to_float(str_):
    numeric_str = ''.join(char for char in str_ if char.isnumeric())
    return Decimal(numeric_str)


def check_url_in_file(url_to_check):
    if not os.path.exists('products_urls.json'):
        with open('products_urls.json', 'w') as file:
            json.dump([], file)
    with open('products_urls.json', 'r') as file:
        json_str = file.read()
    if json_str:
        urls_list = json.loads(json_str)
        if url_to_check in urls_list:
            return True
    return False


def add_url_to_file(file_name, new_url):
    try:
        with open(file_name, 'r') as file:
            json_str = file.read()
    except FileNotFoundError:
        urls_list = []
    else:
        urls_list = json.loads(json_str) if json_str else []
    if new_url not in urls_list:
        urls_list.append(new_url)
    with open(file_name, 'w') as file:
        json.dump(urls_list, file, indent=2)


def read_from_file(file_name):
    with open(file_name, 'r') as f:
        json_str = f.read()
    urls_list = json.loads(json_str) if json_str else []
    return urls_list


def make_img_for_db(image_url):
    image_url = urljoin(dictionaty_urls['shop.kz'], image_url)
    return image_url
    # response = requests.get(image_url)
    # if response.status_code == 200:
    #     return base64.b64encode(response.content).decode('utf-8')


def make_slug_shorter(catalog):
    if catalog.count('-') >= 3:
        catalog = catalog.split('-')
        catalog = '-'.join([catalog[0], catalog[-1]])
        return catalog
    return catalog


def get_category_name(catalog_rus, catalog_url):
    category_name = catalog_url.split('/')
    category_name = [item for item in category_name if item != '']
    catalog_name = make_slug_shorter(category_name[-1])
    category_obj = Category(
        catalog_name=catalog_name,
        catalog_rus=catalog_rus
    )
    return category_obj


def convert_url_to_category_name():
    catalogs_text = ''
    with open('catalogs_urls.json', 'r') as f:
        catalog_urls = json.load(f)
        for catalog_url in catalog_urls:
            catalogs = catalog_url.split('/')
            catalog_name = [catalog for catalog in catalogs if catalog != ''][-1]
            catalogs_text += catalog_name + '\n'
    with open('catalogs.text', 'w') as f:
        f.write(catalogs_text)

'''
if __name__ == '__main__':
    convert_url_to_category_name()
'''

# Функции ниже перенесены из файла parser_main.py

def get_catalog(session, main_url):
    catalogs_urls = []
    response = reload_request(session, 'GET', main_url)
    
    # Парсинг полученного содержимого сайта
    soup = BeautifulSoup(response.text, 'lxml')
    
    div_catalog = soup.find('div', class_='catalog-menu__sidebar').find_all('li')[1:-3]
    urls = [x.find('a')['href'] for x in div_catalog]

    for url in urls:
        catalogs_urls.append(urljoin(main_url, url))
    
    return catalogs_urls

def get_product(session, category_obj, product_url, main_url):
    try:
        response = reload_request(session, 'GET', product_url)
        product_obj = {}
        soup = BeautifulSoup(response.text, 'lxml')
        div_container = soup.find('div', class_='container bx-content-seection')

        title = div_container.find('div', class_='bx-title__container').text.strip()
        product_obj['title'] = title if title else None

        image_url = div_container.find('div', class_='bx_bigimages_imgcontainer').find('span').find('img')['data-src']
        product_obj['image'] = urljoin(main_url, image_url) if image_url else None

        article = div_container.find('ul', class_='bx-card-mark col-lg-4 col-xs-12 col-sm-6').find('li').text.strip()
        product_obj['article'] = article if article else None

        product_obj['exist'] = True
        div_exist = div_container.find('div', class_='bx-item-buttons')
        if div_exist:
            product_obj['exist'] = False if (
                    'Увы, этот товар закончился. Посмотрите другие варианты' in
                    [span.get_text(strip=True) for span in div_exist.find_all('span')]) else True
        product_obj['price_list'] = None
        product_obj['price_in_chain_stores'] = None
        product_obj['price_in_the_online_store'] = None
        product_obj['product_price_of_the_week'] = None
        li_price = div_container.find(
            'div',
            class_='bx-more-prices').find_all('li') if div_container.find('div', class_='bx-more-prices') else None
        
        if li_price:
            price_map = {
                'Цена по прайсу': 'price_list',
                'Цена в магазинах сети': 'price_in_chain_stores',
                'Цена в интернет-магазине': 'price_in_the_online_store',
                'Цена товара недели': 'product_price_of_the_week'
                }
            for price in li_price:
                try:
                    spans = price.find_all('span')
                    product_obj[price_map[spans[0].get_text(strip=True)]] = convert_to_float(spans[1].get_text(strip=True))
                except KeyError as e:
                    logging.exception(e)
                    continue
        divs_details = div_container.find_all('div', class_='bxe-tabs__content')
        div_details = divs_details[0].find_all('div', class_='bx_detail_chars_i') if divs_details[0] else None

        details = {}
        if div_details:
            for div_detail in div_details:
                dt = div_detail.find('dt').get_text(strip=True)
                dd = div_detail.find('dd').get_text(strip=True)
                details[dt] = dd
        product_obj['details'] = json.dumps(details, ensure_ascii=False) if details else None
        product_obj['description'] = divs_details[1].get_text(strip=True) if div_details[1] else None
        product_obj['category_id'] = category_obj.id
        product_obj['url'] = product_url
        product_obj['created_at'] = datetime.now()
        product_obj['updated_at'] = datetime.now()
        logging.info(f'product url: {product_url}')
        return product_obj
    except Exception as e:
        logging.exception(f'{e}, page url:{product_url}')


def get_products(session, category_obj, catalog_products_urls, main_url):
    product_objs = []
    random.shuffle(catalog_products_urls)

    for product_url in catalog_products_urls:
        product_objs.append(get_product(session, category_obj, product_url, main_url))

    bulk_insert_products(product_objs)
    logging.info(f'saved to DB: {product_objs}')

def get_catalog_products(session, catalog_url, main_url):

    print('---> get_catalog_products - 1 <--- ')

    response = reload_request(session, 'GET', catalog_url)
    soup = BeautifulSoup(response.text, 'lxml')
    catalog_rus = soup.find('div', class_='bx-title__container').get_text(strip=True).lower()
    category = get_category_name(catalog_rus, catalog_url)
    category_obj = get_or_create_category(category)
    div_pages = soup.find('div', class_='bx-pagination-container row')

    if div_pages:
        div_pages = div_pages.find('ul').find_all('li')

    total_pages = int(div_pages[-2].text) if div_pages else 1
    page = 2

    print('---> get_catalog_products - 2 <--- ')

    while True:
        dev_products = [div.find('a')['href'] for div in soup.find_all('div', class_='bx_catalog_item_title')]
        catalog_products_urls = [urljoin(main_url, url) for url in dev_products]
        
        logging.info(f'current catalog-page: {catalog_rus} - {page}')
        
        get_products(session, category_obj, catalog_products_urls, main_url)
        
        if page > total_pages:
            break
        
        params = {"PAGEN_1": page}
        response = reload_request(session, 'GET', catalog_url, params=params)
        soup = BeautifulSoup(response.text, 'lxml')
        page += 1
    
    print('---> get_catalog_products - 3 <--- ')


def get_sub_catalog_urls(session, catalog_url, main_url):
    response = reload_request(session, 'GET', catalog_url)
    soup = BeautifulSoup(response.text, 'lxml')
    dev_sub_catalog = soup.find('div', class_='bx_catalog_tile').find_all('li')
    sub_catalog_urls = {}

    for div in dev_sub_catalog:
        sub_catalog_urls[div.text.replace('\n', '')] = urljoin(main_url, div.find('a')['href'])
    
    sub_catalogs_urls = [urljoin(main_url, x.find('a')['href']) for x in dev_sub_catalog]
    return sub_catalogs_urls

def get_sub_catalog_urls_all(session, catalog_url, main_url):
    response = reload_request(session, 'GET', catalog_url)
    soup = BeautifulSoup(response.text, 'lxml')
    sub_catalog_devs = soup.find('div', class_='bx_catalog_tile').find_all('li')
    return sub_catalog_devs

def get_sub_catalogs_urls():
    sub_catalog_urls = {}
        
    session = requests.Session()
    session.headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    })

    main_url = dictionaty_urls['shop.kz']
    
    catalogs_urls = get_catalog(session, main_url)
    random.shuffle(catalogs_urls)
    
    for catalog_url in catalogs_urls:
        sub_catalog_devs = get_sub_catalog_urls_all(session, catalog_url, main_url)
        sub_catalogs_urls = [urljoin(main_url, x.find('a')['href']) for x in sub_catalog_devs]

        random.shuffle(sub_catalogs_urls)

        for sub_catalog_url in sub_catalogs_urls:
            sub_sub_catalog_devs = get_sub_catalog_urls_all(session, sub_catalog_url, main_url)
            for div in sub_sub_catalog_devs:
                sub_catalog_urls[div.text.replace('\n', '')] = urljoin(main_url, div.find('a')['href'])
    
    write_to_file('sub_catalogs_url.json', sub_catalog_urls)
