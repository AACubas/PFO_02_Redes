# servidor.py
from flask import Flask, request, jsonify, g, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import uuid
import os
from functools import wraps
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "tareas.db")

app = Flask(__name__)

#################################
# Helper: base de datos y modelos
#################################
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    # Usuarios
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        token TEXT,
        token_created TEXT
    );
    """)
    # Tareas
    c.execute("""
    CREATE TABLE IF NOT EXISTS tareas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        titulo TEXT NOT NULL,
        descripcion TEXT,
        creada_en TEXT,
        completada INTEGER DEFAULT 0,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    );
    """)
    db.commit()
    db.close()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

################################
# Autenticación con token simple
################################
def generate_token():
    return uuid.uuid4().hex

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Se requiere token de autorización (Bearer)."}), 401
        token = auth_header.split(" ", 1)[1]
        db = get_db()
        cur = db.execute("SELECT * FROM usuarios WHERE token = ?", (token,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "Token inválido o expirado"}), 401
       
        g.current_user = user
        return f(*args, **kwargs)
    return decorated

###########
# Endpoints
###########

# 1) Registro de usuarios
@app.route("/registro", methods=["POST"])
def registro():
    if not request.is_json:
        return jsonify({"error": "Se espera JSON con usuario y contraseña"}), 400
    data = request.get_json()
    usuario = data.get("usuario")
    contraseña = data.get("contraseña")
    if not usuario or not contraseña:
        return jsonify({"error": "Faltan campos 'usuario' o 'contraseña'."}), 400

    password_hash = generate_password_hash(contraseña, method="pbkdf2:sha256", salt_length=16)

    db = get_db()
    try:
        db.execute("INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)",
                   (usuario, password_hash))
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "El nombre de usuario ya existe."}), 409

    return jsonify({"mensaje": f"Usuario '{usuario}' registrado con éxito."}), 201


# 2) Login -> devuelve token simple
@app.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"error": "Se espera JSON con usuario y contraseña"}), 400
    data = request.get_json()
    usuario = data.get("usuario")
    contraseña = data.get("contraseña")
    if not usuario or not contraseña:
        return jsonify({"error": "Faltan campos 'usuario' o 'contraseña'."}), 400

    db = get_db()
    cur = db.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
    user = cur.fetchone()
    if not user:
        return jsonify({"error": "Credenciales incorrectas."}), 401

    if not check_password_hash(user["password_hash"], contraseña):
        return jsonify({"error": "Credenciales incorrectas."}), 401

    # Generar token
    token = generate_token()
    ahora = datetime.utcnow().isoformat()
    db.execute("UPDATE usuarios SET token = ?, token_created = ? WHERE id = ?",
               (token, ahora, user["id"]))
    db.commit()
    return jsonify({"mensaje": "Login OK", "token": token}), 200


# 3) GET /tareas devuelve HTML de bienvenida (requisito)
@app.route("/tareas", methods=["GET"])
def tareas_web():
    html = """
    <!doctype html>
    <html>
      <head><meta charset="utf-8"><title>Bienvenido - Tareas</title></head>
      <body>
        <h1>Bienvenido al Sistema de Gestión de Tareas</h1>
        <p>Para usar la API use los endpoints JSON en /api/tareas y /registro y /login.</p>
      </body>
    </html>
    """
    return make_response(html, 200)

# API REST para manejar tareas (JSON) — protegida con token
@app.route("/api/tareas", methods=["GET"])
@require_auth
def listar_tareas():
    user = g.current_user
    db = get_db()
    cur = db.execute("SELECT id, titulo, descripcion, creada_en, completada FROM tareas WHERE usuario_id = ?",
                     (user["id"],))
    filas = cur.fetchall()
    tareas = []
    for r in filas:
        tareas.append({
            "id": r["id"],
            "titulo": r["titulo"],
            "descripcion": r["descripcion"],
            "creada_en": r["creada_en"],
            "completada": bool(r["completada"])
        })
    return jsonify({"tareas": tareas}), 200

@app.route("/api/tareas", methods=["POST"])
@require_auth
def crear_tarea():
    if not request.is_json:
        return jsonify({"error": "Se espera JSON"}), 400
    data = request.get_json()
    titulo = data.get("titulo")
    descripcion = data.get("descripcion", "")
    if not titulo:
        return jsonify({"error": "El campo 'titulo' es requerido."}), 400
    user = g.current_user
    ahora = datetime.utcnow().isoformat()
    db = get_db()
    cur = db.execute("INSERT INTO tareas (usuario_id, titulo, descripcion, creada_en) VALUES (?, ?, ?, ?)",
                     (user["id"], titulo, descripcion, ahora))
    db.commit()
    tarea_id = cur.lastrowid
    return jsonify({"mensaje": "Tarea creada", "id": tarea_id}), 201

@app.route("/api/tareas/<int:tarea_id>", methods=["PUT"])
@require_auth
def actualizar_tarea(tarea_id):
    if not request.is_json:
        return jsonify({"error": "Se espera JSON"}), 400
    data = request.get_json()
    titulo = data.get("titulo")
    descripcion = data.get("descripcion")
    completada = data.get("completada")  # booleano esperado
    user = g.current_user
    db = get_db()
    # Verificar que la tarea pertenezca al usuario
    cur = db.execute("SELECT * FROM tareas WHERE id = ? AND usuario_id = ?", (tarea_id, user["id"]))
    tarea = cur.fetchone()
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404

    # Construir update dinámico
    fields = []
    values = []
    if titulo is not None:
        fields.append("titulo = ?"); values.append(titulo)
    if descripcion is not None:
        fields.append("descripcion = ?"); values.append(descripcion)
    if completada is not None:
        fields.append("completada = ?"); values.append(1 if completada else 0)
    if not fields:
        return jsonify({"error": "No hay campos para actualizar."}), 400
    values.append(tarea_id)
    sql = f"UPDATE tareas SET {', '.join(fields)} WHERE id = ?"
    db.execute(sql, tuple(values))
    db.commit()
    return jsonify({"mensaje": "Tarea actualizada"}), 200

@app.route("/api/tareas/<int:tarea_id>", methods=["DELETE"])
@require_auth
def borrar_tarea(tarea_id):
    user = g.current_user
    db = get_db()
    cur = db.execute("SELECT * FROM tareas WHERE id = ? AND usuario_id = ?", (tarea_id, user["id"]))
    tarea = cur.fetchone()
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404
    db.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,))
    db.commit()
    return jsonify({"mensaje": "Tarea borrada"}), 200

######
# Main
######
if __name__ == "__main__":
    init_db()
   
    app.run(host="127.0.0.1", port=5000, debug=True)
