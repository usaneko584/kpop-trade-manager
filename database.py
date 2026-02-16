import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Vercelの「Environment Variables」からURLを取得します
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# URLを非同期(asyncpg)用に強制変換する
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0,
        "command_timeout": 30
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session
