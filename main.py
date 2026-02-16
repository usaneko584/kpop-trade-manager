import os
import httpx
from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, engine, Base
from models import Trade

app = FastAPI()

# セッション管理の設定（自分専用の秘密の鍵を設定してください）
app.add_middleware(SessionMiddleware, secret_key="YOUR_SECRET_KEY")
templates = Jinja2Templates(directory="templates")

# LINE設定（Vercelの環境変数に登録してください）
LINE_CHANNEL_ID = os.environ.get("LINE_CHANNEL_ID")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
LINE_REDIRECT_URI = os.environ.get("LINE_REDIRECT_URI") # 例: https://アプリ名.vercel.app/callback

# --- ログイン確認用の関数 ---
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        return None
    return user["user_id"]

# --- 一覧画面（自分のデータだけ出す） ---
@app.get("/")
async def read_root(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = get_current_user(request)
    if not user_id:
        return templates.TemplateResponse("login.html", {"request": request})
    
    # ★ここがポイント：自分の user_id と一致するものだけを取得
    result = await db.execute(
        select(Trade).where(Trade.user_id == user_id).order_by(Trade.id.desc())
    )
    trades = result.scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "trades": trades})

# --- LINEログインの入り口 ---
@app.get("/login")
async def login():
    url = f"https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id={LINE_CHANNEL_ID}&redirect_uri={LINE_REDIRECT_URI}&state=random_state&scope=profile%20openid"
    return RedirectResponse(url)

# --- LINEからの戻り先（コールバック） ---
@app.get("/callback")
async def callback(request: Request, code: str, db: AsyncSession = Depends(get_db)):
    # 1. アクセストークンを取得
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://api.line.me/oauth2/v2.1/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": LINE_REDIRECT_URI,
                "client_id": LINE_CHANNEL_ID,
                "client_secret": LINE_CHANNEL_SECRET,
            },
        )
        token_data = token_res.json()
        
        # 2. ユーザープロフィール（ID）を取得
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        profile_res = await client.get("https://api.line.me/v2/profile", headers=headers)
        profile = profile_res.json()
        
        # 3. セッションに保存してログイン完了
        request.session["user"] = {"user_id": profile["userId"], "name": profile["displayName"]}
        
    return RedirectResponse(url="/")

# --- 新規登録（user_idをセットして保存） ---
@app.post("/create")
async def create_trade(
    request: Request,
    partner_name: str = Form(...),
    give_item: str = Form(None),
    get_item: str = Form(None),
    status: str = Form(...),
    memo: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    user_id = get_current_user(request)
    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    new_trade = Trade(
        user_id=user_id, # ★ログイン中のIDを保存
        partner_name=partner_name,
        give_item=give_item,
        get_item=get_item,
        status=status,
        memo=memo
    )
    db.add(new_trade)
    await db.commit()
    return RedirectResponse(url="/", status_code=303)
