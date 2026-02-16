from sqlalchemy import Column, Integer, String, Date, Text
from database import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    # ★追加：LINEのユーザーIDを保存する列
    user_id = Column(String, index=True, nullable=False) 
    partner_name = Column(String, nullable=False)
    status = Column(String, default="交渉中")
    give_item = Column(String)
    get_item = Column(String)
    shipping_date = Column(Date, nullable=True)
    tracking_number = Column(String, nullable=True)
    memo = Column(Text, nullable=True)
