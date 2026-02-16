import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Vercelの環境変数からURLを取得
DATABASE_URL = os.environ.get("DATABASE_URL")

# URLがない場合の安全策（空文字を入れる）
if DATABASE_URL is None:
    DATABASE_URL = ""

# "postgres://" で始まっていたら "postgresql://" に直す（SQLAlchemy用）
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# エンジン作成
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    connect_args={
        "command_timeout": 30,
        "statement_cache_size": 0  # ★重要：Supabase(Port 6543)にはこれが必須
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session
