"""PFO 2 - Sistema de Gestión de Tareas: API Flask + SQLite."""
import os
import sqlite3

from flask import Flask, g, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
# Clave para firmar la cookie de sesión (en producción, usar variable de entorno)
app.secret_key = os.environ.get("SECRET_KEY", "clave-de-desarrollo-cambiar")
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tareas.db")


# ---------- Base de datos ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def cerrar_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB) as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS usuarios (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   usuario TEXT UNIQUE NOT NULL,
                   password_hash TEXT NOT NULL
               )"""
        )


# ---------- Endpoints ----------
@app.route("/registro", methods=["POST"])
def registro():
    datos = request.get_json(silent=True) or {}
    usuario = (datos.get("usuario") or "").strip()
    password = datos.get("contraseña") or ""

    if not usuario or not password:
        return jsonify({"error": "Faltan 'usuario' y/o 'contraseña'"}), 400

    try:
        get_db().execute(
            "INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)",
            (usuario, generate_password_hash(password)),
        )
        get_db().commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "El usuario ya existe"}), 409

    return jsonify({"mensaje": f"Usuario '{usuario}' registrado"}), 201


@app.route("/login", methods=["POST"])
def login():
    datos = request.get_json(silent=True) or {}
    usuario = (datos.get("usuario") or "").strip()
    password = datos.get("contraseña") or ""

    fila = get_db().execute(
        "SELECT * FROM usuarios WHERE usuario = ?", (usuario,)
    ).fetchone()

    if fila is None or not check_password_hash(fila["password_hash"], password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    session["usuario"] = fila["usuario"]
    return jsonify({"mensaje": f"Bienvenido, {usuario}"}), 200


@app.route("/tareas", methods=["GET"])
def tareas():
    usuario = session.get("usuario")
    if not usuario:
        return jsonify({"error": "Debes iniciar sesión en /login"}), 401

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><title>Tareas</title></head>
<body>
  <h1>¡Bienvenido, {usuario}!</h1>
  <p>Este es tu sistema de gestión de tareas.</p>
</body>
</html>"""


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
