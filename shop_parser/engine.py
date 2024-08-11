from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#from config import settings
from shop_parser.config_old import settings

#from db.models import Base
from shop_parser.models_old import Base

DATABASE_URL = settings.DB_CONN_URL
print(DATABASE_URL)

try:
    engine = create_engine(DATABASE_URL, pool_size=6, echo=False)
    Session = sessionmaker(bind=engine)
except Exception as e:
    print(f'Error [engine.py]: {e}')


def create_db():
    with engine.begin() as connection:
        session = Session(bind=connection)
        Base.metadata.create_all(bind=connection)
        session.commit()
