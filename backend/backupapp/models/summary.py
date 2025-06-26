from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.utils.database import Base

class SummaryHistory(Base):
    __tablename__ = "summary_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id"))
    summary_text = Column(Text)
    original_word_count = Column(Integer)
    summary_word_count = Column(Integer)
    compression_ratio = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document")
