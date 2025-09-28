# 📘 Sistema de Gestión de Tareas (API REST con Flask + SQLite)

## 🌟 Descripción

Este proyecto es un **sistema de gestión de tareas** construido con **Python, Flask y SQLite**.

Permite a los usuarios:

* Registrarse con un nombre de usuario y contraseña (almacenada de forma segura con **hashing**).
* Iniciar sesión y obtener un **token de autenticación**.
* Crear, listar, actualizar y eliminar tareas personales.

La aplicación sigue el modelo **Cliente-Servidor**:

* **Servidor (API Flask):** expone endpoints REST para manejar usuarios y tareas.
* **Cliente (consola en Python o `curl`):** interactúa con la API enviando solicitudes HTTP y recibiendo respuestas JSON.

Requisitos:
- Python 3.8+ (en Linux Mint)
- pip
- Paquetes Python: `Flask`, `requests` (para el cliente)
- SQLite (ya instalado en el sistema)

Instalación rápida:
```bash
python3 -m venv venv
source venv/bin/activate
pip install Flask requests
```
Instrucciones:
* Descargar el repositorio.
* En la carpeta del proyecto correr el servidor (**python3 servidor.py**)
* Puede seguir los ejemplos de las imagenes para ingresar diferentes usuarios o puede activar el client.py desde otra terminal
* Asegurarse de tener activado el entorno virtual (source venv/bin/activate) en ambos terminales

---

## 🚀 Funcionalidades principales

### 🔐 Usuarios

* `POST /registro` → registrar un nuevo usuario.
* `POST /login` → iniciar sesión y obtener un token de acceso.

### 📝 Tareas

* `GET /tareas` → muestra una página HTML de bienvenida.
* `GET /api/tareas` → listar tareas del usuario autenticado.
* `POST /api/tareas` → crear nueva tarea.
* `PUT /api/tareas/<id>` → actualizar una tarea existente.
* `DELETE /api/tareas/<id>` → eliminar una tarea.

---

## 🧪 Ejemplo de uso (flujo)

1. **Registrar usuario**

   ```json
   POST /registro
   {
     "usuario": "nombre",
     "contraseña": "1234"
   }
   ```

   ✅ Respuesta:

   ```json
   {"mensaje": "Usuario 'nombre' registrado con éxito."}
   ```

2. **Login**

   ```json
   POST /login
   {
     "usuario": "nombre",
     "contraseña": "1234"
   }
   ```

   ✅ Respuesta (incluye token):

   ```json
   {"mensaje": "Login OK", "token": "bb9a9c0e0f8345f6a1e8d038e76322b5"}
   ```

3. **Crear tarea**

   ```
   POST /api/tareas
   Header: Authorization: Bearer <TOKEN>
   {
     "titulo": "tomar un litro de agua",
     "descripcion": "Antes de las 18hs"
   }
   ```

   ✅ Respuesta:

   ```json
   {"mensaje": "Tarea creada", "id": 1}
   ```

4. **Listar tareas**

   ```
   GET /api/tareas
   Header: Authorization: Bearer <TOKEN>
   ```

   ✅ Respuesta:

   ```json
   {
     "tareas": [
       {
         "id": 1,
         "titulo": "tomar un litro de agua",
         "descripcion": "Antes de las 18hs",
         "creada_en": "2025-09-27T00:00:00",
         "completada": false
       }
     ]
   }
   ```

---
## 📂 Tecnologías utilizadas

* **Python 3**
* **Flask** (framework web)
* **SQLite** (base de datos ligera)
* **Werkzeug** (hashing seguro de contraseñas)

---

## 📖 Conceptos clave

# 4) Respuestas conceptuales

**¿Por qué hashear contraseñas?**  
Hashear las contraseñas aplica una función unidireccional (hash) para transformar la contraseña en una cadena difícil de invertir. Ventajas:
- Si la base de datos es comprometida, los atacantes no obtienen contraseñas en texto plano por lo que no pueden acceder inmediatamente a las cuentas.
- Usando algoritmos de hashing seguros (p. ej. PBKDF2, bcrypt, Argon2) con sal, se evitan ataques de rainbow tables y se realentizan ataques de fuerza bruta.
- Las aplicaciones verifican contraseñas comparando hashes, no almacenan la contraseña real.

**Ventajas de usar SQLite para este proyecto**  
- Ligero y sin servidor: perfecto para prototipos locales ya que no hay que configurar un servicio DB.
- Almacena los datos en un archivo (`tareas.db`), fácil de versionar o trasladar.
- Suficiente para cargas pequeñas y pruebas; además se integra muy bien con Python (`sqlite3` estándar).
