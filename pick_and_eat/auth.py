from passlib.context import CryptContext
from jose import JWTError,jwt
from datetime import datetime,timedelta
SECRET_KEY = "superkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"],deprecated = "auto")

def hash_password(password:str):
    return pwd_context.hash(password[:72])
def verify_password(plain_password:str,hashed_password:str):
    return pwd_context.verify(plain_password,hashed_password)
def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt