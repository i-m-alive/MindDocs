from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.utils.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    domain = Column(String, nullable=False)
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    blob_url = Column(String, nullable=True)  # ✅ Add this line
    created_at = Column(DateTime(timezone=True), server_default=func.now())
