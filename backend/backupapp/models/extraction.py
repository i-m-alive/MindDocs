from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.utils.database import Base

class DocumentExtraction(Base):
    __tablename__ = "document_extraction"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id"))
    domain = Column(String(50))
    extracted_fields = Column(JSON)  # Dictionary of key-values
    raw_text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document")
