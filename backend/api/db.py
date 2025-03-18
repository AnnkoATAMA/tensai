from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URL = "mysql+aiomysql://brachion:password@mysql:3306/brachion"

async_engine = create_async_engine(DB_URL, echo=True)
async_session = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)

Base = declarative_base()

async def get_db():
    async with async_session() as session:
        yield session