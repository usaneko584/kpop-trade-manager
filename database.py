import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# ★ここを「直接記入」から「環境変数の読み込み」に戻します
DATABASE_URL = os.environ.get("DATABASE_URL")

# もしURLが postgres:// で始まっていたら postgresql:// に直す処理（念のため）
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# エンジン作成（statement_cache_size: 0 は残します！）
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    connect_args={
        "command_timeout": 30,
        "statement_cache_size": 0  # ← ポート6543接続に必須
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session
