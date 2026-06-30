from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from backend.database import Base

class Sound(Base):
    __tablename__ = "sounds"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    category = Column(String, default="")
    tags = Column(String, default="")
    cover_image = Column(String, nullable=True)
    shortcut_key = Column(String, nullable=True)
    is_pinned = Column(Boolean, default=False)
    play_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    order = Column(Integer, default=0)

class Setting(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=True)
