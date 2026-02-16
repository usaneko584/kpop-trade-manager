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
