from fastapi import FastAPI, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, engine, Base
from sqlalchemy import Column, Integer, String, Date, Text
from database import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    partner_name = Column(String, nullable=False) # 相手の名前
    status = Column(String, default="交渉中")     # ステータス
    give_item = Column(String)                    # 譲（自分のカード）
    get_item = Column(String)                     # 求（相手のカード）
    shipping_date = Column(Date, nullable=True)   # 発送日
    tracking_number = Column(String, nullable=True) # 追跡番号
    memo = Column(Text, nullable=True)            # メモ

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- 一覧画面 ---
@app.get("/")
async def read_root(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trade).order_by(Trade.id.desc()))
    trades = result.scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "trades": trades})

# --- 新規登録画面 ---
@app.get("/create")
async def show_create_form(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

@app.post("/create")
async def create_trade(
    partner_name: str = Form(...),
    give_item: str = Form(None),
    get_item: str = Form(None),
    status: str = Form(...),
    memo: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    new_trade = Trade(partner_name=partner_name, give_item=give_item, get_item=get_item, status=status, memo=memo)
    db.add(new_trade)
    await db.commit()
    return RedirectResponse(url="/", status_code=303)

# --- ★追加：詳細・編集画面 (表示) ---
@app.get("/detail/{trade_id}")
async def show_detail(trade_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    # IDでデータを検索
    trade = await db.get(Trade, trade_id)
    return templates.TemplateResponse("detail.html", {"request": request, "trade": trade})

# --- ★追加：更新処理 (保存) ---
@app.post("/update/{trade_id}")
async def update_trade(
    trade_id: int,
    partner_name: str = Form(...),
    give_item: str = Form(None),
    get_item: str = Form(None),
    status: str = Form(...),
    tracking_number: str = Form(None),
    memo: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    trade = await db.get(Trade, trade_id)
    if trade:
        # データを書き換える
        trade.partner_name = partner_name
        trade.give_item = give_item
        trade.get_item = get_item
        trade.status = status
        trade.tracking_number = tracking_number
        trade.memo = memo
        await db.commit()
    return RedirectResponse(url="/", status_code=303)

# --- ★追加：削除処理 ---
@app.get("/delete/{trade_id}")
async def delete_trade(trade_id: int, db: AsyncSession = Depends(get_db)):
    trade = await db.get(Trade, trade_id)
    if trade:
        await db.delete(trade)
        await db.commit()
    return RedirectResponse(url="/", status_code=303)