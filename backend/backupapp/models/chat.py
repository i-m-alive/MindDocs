from sqlalchemy import Column, Integer, Text, String, ForeignKey
from app.utils.database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    doc_id = Column(Integer, ForeignKey("documents.id"))
    question = Column(Text)
    answer = Column(Text)
    domain = Column(String(50))
