from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite+aiosqlite:///./soundboard.db"

settings = Settings()

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        result = await conn.exec_driver_sql("PRAGMA table_info(sounds)")
        columns = [row[1] for row in result.fetchall()]
        if "volume" not in columns:
            await conn.exec_driver_sql("ALTER TABLE sounds ADD COLUMN volume FLOAT DEFAULT 1.0")
        if "file_hash" not in columns:
            await conn.exec_driver_sql("ALTER TABLE sounds ADD COLUMN file_hash VARCHAR")

async def get_db():
    async with async_session() as session:
        yield session
