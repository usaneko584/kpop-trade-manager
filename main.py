@app.get("/")
async def read_root(request: Request, search: str = None, db: AsyncSession = Depends(get_db)):
    user = get_user(request)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    # 基本の検索：自分のデータだけ
    query = select(Trade).where(Trade.user_id == user["user_id"])
    
    # 検索ワードがあれば絞り込み
    if search:
        query = query.where(
            (Trade.partner_name.contains(search)) | 
            (Trade.give_item.contains(search)) | 
            (Trade.get_item.contains(search))
        )
    
    result = await db.execute(query.order_by(Trade.id.desc()))
    trades = result.scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "trades": trades, "user": user, "search": search})
