import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Vercelの環境変数からURLを取得
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# SQLAlchemyを非同期(asyncpg)に対応させるためのURL変換
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# ★ここが重要：SupabaseのTransaction Poolerに対応させるための設定を追加
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "prepared_statement_cache_size": 0,  # 下準備のキャッシュを無効化
        "statement_cache_size": 0,           # ステートメントキャッシュを無効化
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session
