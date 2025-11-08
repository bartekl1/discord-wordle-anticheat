from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models import Base

engine = None
AsyncSessionLocal = None

async def init_db(database_url: str):
    global engine, AsyncSessionLocal
    engine = create_async_engine(database_url, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
