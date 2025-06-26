from passlib.context import CryptContext

# Define the encryption context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash the password using bcrypt
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verify if the plain password matches the hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
