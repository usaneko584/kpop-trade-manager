from sqlalchemy import Column, Integer, String, Date, Text, Boolean
from database import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False) 
    partner_name = Column(String, nullable=False)
    status = Column(String, default="交渉中")
    give_artist = Column(String)
    give_item = Column(String)
    get_artist = Column(String)
    get_item = Column(String)
    give_image_url = Column(String, nullable=True)
    get_image_url = Column(String, nullable=True) 
    is_public = Column(Boolean, default=False) 
    shipping_date = Column(Date, nullable=True)
    tracking_number = Column(String, nullable=True)
    memo = Column(Text, nullable=True)
