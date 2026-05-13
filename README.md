# SMAT

Proyecto monorepo con backend FastAPI y móvil Flutter para gestión de estaciones.

## Arranque rápido

### Backend

1. Ir al directorio del backend.
2. Instalar dependencias de Python si hace falta.
3. Ejecutar:

```bash
uvicorn app.main:app --reload
```

### Móvil

1. Ir al directorio `mobile`.
2. Obtener dependencias de Flutter si hace falta.
3. Ejecutar:

```bash
flutter run
```

## Acceso por defecto

- Usuario: `admin`
- Contraseña: `admin`

## Notas

- Si corres el móvil en Android Emulator, la app apunta al backend en `10.0.2.2`.
- Si corres en web o escritorio, usa `127.0.0.1`.
- Si necesitas otra dirección, define `SMAT_API_URL` al compilar o ejecutar.
