from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from . import models

SECRET_KEY = "UNMSM_FISI_SMAT_2026"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def obtener_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def crear_token(data: dict):
    expiracion = datetime.utcnow() + timedelta(minutes=60)
    data.update({"exp": expiracion})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def autenticar_usuario(db: Session, username: str, password: str):
    user = db.query(models.UsuarioDB).filter(models.UsuarioDB.username == username).first()
    if not user:
        return False
    if not verificar_password(password, user.password_hash):
        return False
    return user

def validar_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Token inválido")