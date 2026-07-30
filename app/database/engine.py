from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import MYSQL_URL


engine = create_async_engine(
    MYSQL_URL,
    pool_pre_ping=False,
    pool_recycle=3600,
    echo=False
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)