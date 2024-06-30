import logging

# TODO: Что за модуль?
#import DatabaseManager

#from datetime import datetime

from shop_parser.db.engine import Session

from db.models import Product, Category
#from shop_parser.db.models_old import Product, Category

def get_or_create_category(category: Category):
    try:
        with Session() as session:
            category_obj = session.query(Category).filter_by(catalog_name=category.catalog_name).first()
            if category_obj:
                return category_obj
            else:
                new_category = Category(
                    catalog_name=category.catalog_name,
                    catalog_rus=category.catalog_rus
                )
                session.add(new_category)
                session.commit()
                new_category = session.query(Category).filter_by(catalog_name=category.catalog_name).first()
                return new_category
    except Exception as e:
        logging.exception(e)
        print(f"Error in [get_or_create_category]: {e}")


def bulk_insert_products(products_data: list):

    '''
    TODO: Здесь происодит ошибка при повторяющемся ключе
    
    '''
    
    try:
        with Session() as session:
            products_instances = [Product(**data) for data in products_data]
            session.bulk_save_objects(products_instances)
            session.commit()
    except Exception as e:
        logging.exception(f"Error in [bulk_insert_products]: {e}")
        #print(f"Error in [bulk_insert_products]: {e}")


# TODO: Ниже вставлены функции из модуля shop_parser/crud_old.py

def create_table_product():
    with DatabaseManager() as cursor:
        try:
            cursor.execute('''CREATE TABLE IF NOT EXISTS product (
                id SERIAL PRIMARY KEY,
                exist BOOLEAN,
                title VARCHAR(150) UNIQUE,
                image VARCHAR(150),
                article VARCHAR(100) UNIQUE,
                price_list NUMERIC(10, 2),
                price_in_chain_stores NUMERIC(10, 2),
                price_in_the_online_store NUMERIC(10, 2),
                product_price_of_the_week NUMERIC(10, 2),
                details JSON,
                description TEXT,
                url TEXT UNIQUE,
                category_name JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                  )''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_title_article_url ON product (title, article, url);''')
        except Exception as e:
            print(f"Error in [create_table_product]: {e}")


def create_table_category():
    with DatabaseManager() as cursor:
        try:
            cursor.execute('''CREATE TABLE IF NOT EXISTS product (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE,
                category_name JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                  )''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_name ON product (name);''')
        except Exception as e:
            print(f"Error in [create_table_category]: {e}")


def insert_categories(categories):
    with DatabaseManager() as cursor:
        try:
            insert_query = '''INSERT INTO categories (
                                name,
                                category_name,
                                created_at,
                                updated_at) 
                                    VALUES (%s, %s, %s, %s)
                                    ON CONFLICT (name) DO NOTHING;'''
            cursor.executemany(insert_query, [(p['name'],
                                               p['category_name'],
                                               p['created_at'],
                                               p['updated_at']
                                               ) for c in categories])
        except Exception as e:
            print(f"Error in [insert_categories]: {e}")

"""
def bulk_insert_products(products):
    with DatabaseManager() as cursor:
        try:
            insert_query = '''INSERT INTO product (
                                exist,
                                title,
                                image,
                                article,
                                price_list,
                                price_in_chain_stores,
                                price_in_the_online_store,
                                product_price_of_the_week,
                                details,
                                category_name,
                                description,
                                url,
                                created_at,
                                updated_at) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (title) DO NOTHING;'''
            cursor.executemany(insert_query, [(p['exist'],
                                               p['title'],
                                               p['image'],
                                               p['article'],
                                               p['price_list'],
                                               p['price_in_chain_stores'],
                                               p['price_in_the_online_store'],
                                               p['product_price_of_the_week'],
                                               p['details'],
                                               p['category_name'],
                                               p['description'],
                                               p['url'],
                                               p['created_at'],
                                               p['updated_at']
                                               ) for p in products])
        except Exception as e:
            print(f"Error in [bulk_insert_products]: {e}")
"""
            