#import json
import logging
import random
import time
import requests

from datetime       import datetime
#from urllib.parse   import urljoin
#from bs4            import BeautifulSoup

#from shop_parser.crud import bulk_insert_products, get_or_create_category
from shop_parser.engine import create_db

#from utils.utils_parser import reload_request, convert_to_float, get_category_name, write_to_file
from utils.utils_parser import get_catalog, get_sub_catalog_urls, get_catalog_products, dictionaty_urls as urls

main_url = urls['shop.kz']

def main():
    #try:
    print('start: create_db')
    create_db()
    
    print('create session')
    session = requests.Session()

    print('update')
    session.headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    })

    print('get_catalog')
    catalogs_urls = get_catalog(session, main_url)
    #catalogs_urls = get_catalog()
    
    print('updashufflee')
    random.shuffle(catalogs_urls)
    
    print('Pause 1')
    time.sleep(2)

    print(f'len catalogs_urls - {len(catalogs_urls)}')

    for catalog_url in catalogs_urls:
        sub_catalogs_urls = get_sub_catalog_urls(session, catalog_url, main_url)
        print(f'len sub_catalogs_urls - {len(sub_catalogs_urls)}')


        print('Pause 2 -1')
        time.sleep(1)
        random.shuffle(sub_catalogs_urls)
        
        for sub_catalog_url in sub_catalogs_urls:
            sub_sub_catalogs_urls = get_sub_catalog_urls(session, sub_catalog_url, main_url)
            print(f'len sub_sub_catalogs_urls - {len(sub_sub_catalogs_urls)}')

            print('Pause 2 -2')
            time.sleep(1)

            logging.info('len sub_sub_catalogs_urls: f{len(sub_sub_catalogs_urls)}')
            
            # TODO: Перетасовка списка с помощью функции shuffle - нужна ли?
            random.shuffle(sub_sub_catalogs_urls)
            
            for sub_sub_catalog_url in sub_sub_catalogs_urls:
                get_catalog_products(session, sub_sub_catalog_url, main_url)

                print('Pause 2 -3')
                time.sleep(1)

            delay = random.uniform(1, 3)
            time.sleep(delay)

    print('Pause 3')
    #time.sleep(10)
    logging.info(f'Parsing finish: {datetime.now().time()}')
    '''
    except Exception as e:
        print(f'Main Exception : {e}')
        logging.error(f'Main Exception : {e}')
    '''

if __name__ == '__main__':
    logging.basicConfig(
        filename="logs/shopkz.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
    )
    main()
