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

### 🔑 ¿Por qué hashear contraseñas?

* Nunca se guardan en texto plano.
* Si la base de datos se filtra, el atacante no obtiene la contraseña real por lo que se puede preservar la información de los usuarios.
* Con hashing seguro + sal, se dificulta la fuerza bruta o rainbow tables.

### 💾 Ventajas de usar SQLite

* Base de datos ligera y portable (un solo archivo `.db`).
* No requiere servidor adicional.
* Fácil de integrar con Python (librería estándar `sqlite3`).
