from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "UNMSM_FISI_SMAT_2026"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"

def crear_token(data: dict):
    expiracion = datetime.utcnow() + timedelta(minutes=60)
    data.update({"exp": expiracion})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def autenticar_usuario(username: str, password: str) -> bool:
    return username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD

def validar_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Token inválido")