from sqlalchemy import Column, Integer, String
from app.utils.database import Base

# SQLAlchemy model representing users in the database
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    domain = Column(String(50), nullable=True)