from datetime import datetime, timedelta
from jose import jwt  # JOSE == Javascript Object Signing & Encryption

# ⚠️ Change this in production and store securely (e.g., .env)
SECRET_KEY = "4c7ef60ee916e605a791ef8b5518bc2de555e50bb3b4f6bbb4ea4a3fb753098b"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Create the JWT access token
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()  # typically contains {"sub": username}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
