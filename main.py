import os
import httpx
from fastapi import FastAPI, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, engine, Base
from models import Trade

app = FastAPI()

# セッション設定
app.add_middleware(SessionMiddleware, secret_key="rena_trading_secret_key")
templates = Jinja2Templates(directory="templates")

# 環境変数
LINE_CHANNEL_ID = os.environ.get("LINE_CHANNEL_ID")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
LINE_REDIRECT_URI = os.environ.get("LINE_REDIRECT_URI")

# テーブル作成
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ログインユーザー取得
def get_user(request: Request):
    return request.session.get("user")

# --- ルーティング ---

@app.get("/")
async def read_root(request: Request, db: AsyncSession = Depends(get_db)):
    user = get_user(request)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    result = await db.execute(
        select(Trade).where(Trade.user_id == user["user_id"]).order_by(Trade.id.desc())
    )
    trades = result.scalars().all()
    # テンプレートにuser情報を渡す
    return templates.TemplateResponse("index.html", {"request": request, "trades": trades, "user": user})

@app.get("/login")
async def login_gate():
    url = f"https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id={LINE_CHANNEL_ID}&redirect_uri={LINE_REDIRECT_URI}&state=random_state&scope=profile%20openid"
    return RedirectResponse(url)

@app.get("/callback")
async def callback(request: Request, code: str):
    async with httpx.AsyncClient() as client:
        # トークン取得
        token_res = await client.post("https://api.line.me/oauth2/v2.1/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": LINE_REDIRECT_URI,
            "client_id": LINE_CHANNEL_ID, "client_secret": LINE_CHANNEL_SECRET
        })
        # プロフィール取得
        headers = {"Authorization": f"Bearer {token_res.json()['access_token']}"}
        profile_res = await client.get("https://api.line.me/v2/profile", headers=headers)
        profile = profile_res.json()
        
        # ★セッション保存（pictureUrlを画像として追加）
        request.session["user"] = {
            "user_id": profile["userId"], 
            "name": profile["displayName"],
            "picture": profile.get("pictureUrl") # 画像URLを保存
        }
    return RedirectResponse(url="/")

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

# --- 取引操作 ---

@app.get("/create")
async def show_create(request: Request):
    user = get_user(request)
    if not user: return RedirectResponse(url="/")
    return templates.TemplateResponse("create.html", {"request": request, "user": user})

@app.post("/create")
async def create_trade(request: Request, partner_name: str = Form(...), give_item: str = Form(None), 
                       get_item: str = Form(None), status: str = Form(...), memo: str = Form(None), 
                       db: AsyncSession = Depends(get_db)):
    user = get_user(request)
    if not user: return RedirectResponse(url="/")
    
    new_trade = Trade(user_id=user["user_id"], partner_name=partner_name, give_item=give_item, 
                      get_item=get_item, status=status, memo=memo)
    db.add(new_trade)
    await db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/detail/{trade_id}")
async def show_detail(trade_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = get_user(request)
    if not user: return RedirectResponse(url="/")
    result = await db.execute(select(Trade).where(Trade.id == trade_id, Trade.user_id == user["user_id"]))
    trade = result.scalars().first()
    return templates.TemplateResponse("detail.html", {"request": request, "trade": trade, "user": user})

@app.post("/update/{trade_id}")
async def update_trade(trade_id: int, request: Request, partner_name: str = Form(...), 
                       status: str = Form(...), tracking_number: str = Form(None), 
                       memo: str = Form(None), db: AsyncSession = Depends(get_db)):
    user = get_user(request)
    result = await db.execute(select(Trade).where(Trade.id == trade_id, Trade.user_id == user["user_id"]))
    trade = result.scalars().first()
    if trade:
        trade.partner_name = partner_name
        trade.status = status
        trade.tracking_number = tracking_number
        trade.memo = memo
        await db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/delete/{trade_id}")
async def delete_trade(trade_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = get_user(request)
    result = await db.execute(select(Trade).where(Trade.id == trade_id, Trade.user_id == user["user_id"]))
    trade = result.scalars().first()
    if trade:
        await db.delete(trade)
        await db.commit()
    return RedirectResponse(url="/", status_code=303)
