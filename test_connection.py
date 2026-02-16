import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# .envを読み込む
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# URLの補正
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
     DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

async def test_connect():
    print("⏳ 接続テストを開始します...")
    if not DATABASE_URL:
        print("❌ エラー: .envファイルにDATABASE_URLが設定されていません。")
        return
    
    try:
        # 接続の試行
        engine = create_async_engine(DATABASE_URL)
        async with engine.connect() as conn:
            print("✅ 接続成功！データベースと通信できています。")
    except Exception as e:
        print(f"❌ 接続失敗... エラー内容:\n{e}")

if __name__ == "__main__":
    asyncio.run(test_connect())