from sqlalchemy import Column, Integer, String, Date, Text
from database import Base

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # ★誰のデータか保存する列を追加
    partner_name = Column(String, nullable=False)

    id = Column(Integer, primary_key=True, index=True)
    partner_name = Column(String, nullable=False)
    status = Column(String, default="交渉中")
    give_item = Column(String)
    get_item = Column(String)
    shipping_date = Column(Date, nullable=True)
    tracking_number = Column(String, nullable=True)
    memo = Column(Text, nullable=True)
