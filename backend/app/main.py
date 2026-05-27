from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, auth, database

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI(title="SMAT API - Unidad I")


class LoginRequest(BaseModel):
    username: str
    password: str

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|10\.0\.2\.2)(:\d+)?",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.post("/register", status_code=status.HTTP_201_CREATED, tags=["Seguridad"])
def register(user: schemas.UsuarioCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.UsuarioDB).filter(models.UsuarioDB.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
    
    hashed_password = auth.obtener_password_hash(user.password)
    nuevo_usuario = models.UsuarioDB(username=user.username, password_hash=hashed_password)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"status": "Usuario registrado exitosamente"}

@app.post("/token", tags=["Seguridad"])
def login(credentials: LoginRequest, db: Session = Depends(database.get_db)):
    usuario = auth.autenticar_usuario(db, credentials.username, credentials.password)
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    return {
        "access_token": auth.crear_token({"sub": usuario.username}),
        "token_type": "bearer",
    }

@app.get("/estaciones/", response_model=list[schemas.EstacionConLectura], tags=["SMAT"])
def listar_estaciones(db: Session = Depends(database.get_db)):
    estaciones = db.query(models.EstacionDB).all()
    resultado = []
    for estacion in estaciones:
        ultima_lectura = None
        if estacion.lecturas:
            ultima = max(estacion.lecturas, key=lambda lectura: lectura.fecha)
            ultima_lectura = ultima.valor
        resultado.append(
            {
                "id": estacion.id,
                "nombre": estacion.nombre,
                "ubicacion": estacion.ubicacion,
                "ultima_lectura": ultima_lectura,
            }
        )
    return resultado

@app.post("/estaciones/", tags=["SMAT"])
def crear_estacion(estacion: schemas.EstacionCreate, db: Session = Depends(database.get_db), user=Depends(auth.validar_token)):
    nueva = models.EstacionDB(**estacion.dict())
    db.add(nueva)
    db.commit()
    return nueva


@app.put("/estaciones/{estacion_id}", tags=["SMAT"])
def editar_estacion(
    estacion_id: int,
    estacion: schemas.EstacionCreate,
    db: Session = Depends(database.get_db),
    user=Depends(auth.validar_token),
):
    estacion_db = db.query(models.EstacionDB).filter(models.EstacionDB.id == estacion_id).first()
    if not estacion_db:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    estacion_db.nombre = estacion.nombre
    estacion_db.ubicacion = estacion.ubicacion
    db.commit()
    db.refresh(estacion_db)
    return estacion_db


@app.delete("/estaciones/{estacion_id}", tags=["SMAT"])
def eliminar_estacion(
    estacion_id: int,
    db: Session = Depends(database.get_db),
    user=Depends(auth.validar_token),
):
    estacion_db = db.query(models.EstacionDB).filter(models.EstacionDB.id == estacion_id).first()
    if not estacion_db:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    db.delete(estacion_db)
    db.commit()
    return {"status": "Estación eliminada"}

@app.post("/lecturas/", tags=["Telemetría"])
def registrar_lectura(lectura: schemas.LecturaCreate, db: Session = Depends(database.get_db), user=Depends(auth.validar_token)):
    # Reto Maestro: Validación de existencia
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == lectura.estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    nueva_lectura = models.LecturaDB(**lectura.dict())
    db.add(nueva_lectura)
    db.commit()
    return {"status": "Lectura registrada con éxito"}