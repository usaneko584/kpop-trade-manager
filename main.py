import os
import httpx
from fastapi import FastAPI, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.future import select
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, engine, Base
from models import Trade

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="rena_kpop_manager_secure")
templates = Jinja2Templates(directory="templates")

LINE_CHANNEL_ID = os.environ.get("LINE_CHANNEL_ID")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
LINE_REDIRECT_URI = os.environ.get("LINE_REDIRECT_URI")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def get_user(request: Request):
    return request.session.get("user")

@app.get("/")
async def read_root(request: Request, search: str = None, db: AsyncSession = Depends(get_db)):
    user = get_user(request)
    if not user: return templates.TemplateResponse("login.html", {"request": request})
    query = select(Trade).where(Trade.user_id == user["user_id"])
    if search:
        query = query.where(or_(
            Trade.partner_name.contains(search), 
            Trade.give_artist.contains(search),
            Trade.get_artist.contains(search),
            Trade.give_item.contains(search), 
            Trade.get_item.contains(search)
        ))
    result = await db.execute(query.order_by(Trade.id.desc()))
    trades = result.scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "trades": trades, "user": user, "search": search})

@app.get("/create")
async def show_create(request: Request):
    user = get_user(request)
    if not user: return RedirectResponse(url="/")
    return templates.TemplateResponse("create.html", {"request": request, "user": user})

@app.post("/create")
async def create_trade(
    request: Request, 
    partner_name: str = Form(...), 
    give_artist: str = Form(None), 
    give_item: str = Form(None), 
    get_artist: str = Form(None), 
    get_item: str = Form(None), 
    status: str = Form(...), 
    memo: str = Form(None), 
    is_public: str = Form("false"), 
    db: AsyncSession = Depends(get_db)
):
    user = get_user(request)
    if not user: return RedirectResponse(url="/", status_code=303)

    new_trade = Trade(
        user_id=user["user_id"],
        partner_name=partner_name,
        give_artist=give_artist,
        give_item=give_item,
        get_artist=get_artist,
        get_item=get_item,
        status=status,
        memo=memo,
        is_public=(is_public == "true")
    )
    db.add(new_trade)
    await db.commit()
    return RedirectResponse(url="/", status_code=303)

# ... update_trade など、残りの関数はこれまでの修正版をそのままお使いください ...
