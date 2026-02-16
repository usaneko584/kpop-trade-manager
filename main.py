from fastapi import FastAPI, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, engine, Base
from models import Trade 

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 起動時にテーブルを作成
@app.on_event("startup")
async def startup():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Startup error: {e}")

# --- 一覧画面 ---
@app.get("/")
async def read_root(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trade).order_by(Trade.id.desc()))
    trades = result.scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "trades": trades})

# --- 新規登録 ---
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

# --- 詳細・編集 ---
@app.get("/detail/{trade_id}")
async def show_detail(trade_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    trade = result.scalars().first()
    return templates.TemplateResponse("detail.html", {"request": request, "trade": trade})

# --- 更新 ---
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
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    trade = result.scalars().first()
    if trade:
        trade.partner_name = partner_name
        trade.give_item = give_item
        trade.get_item = get_item
        trade.status = status
        trade.tracking_number = tracking_number
        trade.memo = memo
        await db.commit()
    return RedirectResponse(url="/", status_code=303)

# --- 削除 ---
@app.get("/delete/{trade_id}")
async def delete_trade(trade_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    trade = result.scalars().first()
    if trade:
        await db.delete(trade)
        await db.commit()
    return RedirectResponse(url="/", status_code=303)
