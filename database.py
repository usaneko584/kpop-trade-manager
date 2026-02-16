from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from pathlib import Path

# 確実に .env を読み込む
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# 修正前：DATABASE_URL = os.environ.get("DATABASE_URL")
# ↓ 修正後（これをコピペしてください）

DATABASE_URL = "postgresql://postgres:k7R0D8AmIrbQ8egW@db.loleqhlyenrbroqilgtk.supabase.co:6543/postgres"

# URLの修正
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# エンジン作成部分（ここはそのまま、statement_cache_sizeが入っていることを確認）
engine = create_async_engine(
    DATABASE_URL, 
    echo=True,
    pool_pre_ping=True,
    connect_args={
        "command_timeout": 30,
        "statement_cache_size": 0  # ← ポート6543にはこれが絶対必要！
    }
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
