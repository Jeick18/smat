# SMAT (Sistema de Monitorización y Alerta Temprana)

## Arquitectura
El repositorio está dividido en tres componentes principales:

- **`backend/`**: API RESTful construida con FastAPI que gestiona la base de datos, la autenticación y la recepción de datos de telemetría.
- **`iot_device/`**: Script de emulación IoT en Python para simular sensores (ej. niveles de agua) y enviar telemetría, incluyendo lógica de frecuencia dinámica y alertas.
- **`mobile/`**: Aplicación hecha en Flutter para la visualización de estaciones, métricas en tiempo real y gestión de usuarios.

## Tecnologías Principales

- **Backend**: Python, FastAPI, Uvicorn.
- **Móvil/Frontend**: Flutter, Dart.
- **IoT**: Python, Requests.

---

## Guía de Instalación y Uso

### 1. Backend (FastAPI)

1. Ingresa al directorio del backend:
   ```bash
   cd backend
   ```
2. Crea y activa un entorno virtual de Python:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requeriments.txt
   ```
4. Ejecuta el servidor:
   ```bash
   uvicorn app.main:app --reload
   ```

### 2. Aplicación Móvil (Flutter)

1. Ingresa al directorio móvil:
   ```bash
   cd mobile
   ```
2. Instala las dependencias de Flutter:
   ```bash
   flutter pub get
   ```
3. Ejecuta la aplicación:
   ```bash
   flutter run
   ```

### 3. Dispositivo IoT

El script de IoT emula un hardware de sensor que reporta telemtría a la nube. Para asegurar la comunicación, se utiliza un Token JWT, el cual valida la identidad del dispositivo en el backend inyectándose en las cabeceras (headers) de cada petición HTTP.

1. Ingresa al directorio del IoT:
   ```bash
   cd iot_device
   ```
2. Crea y activa un entorno virtual de Python:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requeriments.txt
   ```
4. Ejecuta el emulador (asegúrate de que el backend esté corriendo):
   ```bash
   python sensor_emitter.py
   ```

## Notas de Conectividad

- **Emulador Android**: Si usas el emulador de Android, la app apuntará por defecto al backend en `10.0.2.2`.
- **Web / Escritorio**: Si corres en Web, Linux o iOS, usará por defecto `127.0.0.1`.
- **Personalización de IP** (ej. pruebas en dispositivo físico): Define la variable `SMAT_API_URL` al momento de ejecutar:
  ```bash
  flutter run --dart-define=SMAT_API_URL=http://<IP_LOCAL>:8000
  ```
