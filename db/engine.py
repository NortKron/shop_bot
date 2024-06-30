from config import settings
from db.models import Base

# Base = declarative_base()
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = settings.DB_CONN_URL

try:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(bind=engine, class_=AsyncSession)
except Exception as e:
    print(f'Module engine.py : {e}')

async def create_db():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
