import os
from environs import Env

env = Env()
env.read_env()

class Settings:
    def __init__(self):

        '''
        self.POSTGRES_DB = env.str("POSTGRES_DB")
        self.POSTGRES_USER = env.str("POSTGRES_USER")
        self.POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD")
        self.POSTGRES_PORT = env.str("POSTGRES_PORT")
        self.POSTGRES_HOST = env.str("POSTGRES_HOST")
        self.DB_CONN_URL = f'postgresql+psycopg2://{env.str("POSTGRES_USER")}:{env.str("POSTGRES_PASSWORD")}@{env.str("POSTGRES_HOST")}:{env.str("POSTGRES_PORT")}/{env.str("POSTGRES_DB")}'
        '''
        self.BOT_TOKEN = '5651945723:AAHfGimBOHaJ7DU2Spoei7YwWs5WsifR-7M'
        self.POSTGRES_DB = 'Shop_Bot'
        self.POSTGRES_USER = 'postgres'
        self.POSTGRES_PASSWORD = '4231'
        self.POSTGRES_PORT = '5432'
        self.POSTGRES_HOST = 'localhost'
        self.DB_CONN_URL = f'postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

settings = Settings()
os.makedirs("logs", exist_ok=True)
