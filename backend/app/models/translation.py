from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.utils.database import Base

class TranslationHistory(Base):
    __tablename__ = "translation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id"))
    original_language = Column(String(30))
    target_language = Column(String(30))
    translated_text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document")
