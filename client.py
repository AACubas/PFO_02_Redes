# client.py
import requests
import sys

API_BASE = "http://127.0.0.1:5000"
TOKEN = None

def register():
    usuario = input("Usuario: ").strip()
    contraseña = input("Contraseña: ").strip()
    r = requests.post(f"{API_BASE}/registro", json={"usuario": usuario, "contraseña": contraseña})
    print(r.status_code, r.json())

def login():
    global TOKEN
    usuario = input("Usuario: ").strip()
    contraseña = input("Contraseña: ").strip()
    r = requests.post(f"{API_BASE}/login", json={"usuario": usuario, "contraseña": contraseña})
    if r.status_code == 200:
        TOKEN = r.json().get("token")
        print("Login OK. Token guardado en memoria.")
    else:
        print("Error:", r.status_code, r.json())

def list_tareas():
    if not TOKEN:
        print("Hacé login primero.")
        return
    headers = {"Authorization": f"Bearer {TOKEN}"}
    r = requests.get(f"{API_BASE}/api/tareas", headers=headers)
    print(r.status_code, r.json())

def crear_tarea():
    if not TOKEN:
        print("Hacé login primero.")
        return
    titulo = input("Título: ").strip()
    descripcion = input("Descripción: ").strip()
    headers = {"Authorization": f"Bearer {TOKEN}"}
    r = requests.post(f"{API_BASE}/api/tareas", headers=headers, json={"titulo": titulo, "descripcion": descripcion})
    print(r.status_code, r.json())

def actualizar_tarea():
    if not TOKEN:
        print("Hacé login primero.")
        return
    tarea_id = input("ID de tarea a actualizar: ").strip()
    titulo = input("Nuevo título (enter para no cambiar): ").strip()
    descripcion = input("Nueva descripción (enter para no cambiar): ").strip()
    completada = input("Completada? (s/n/enter para no cambiar): ").strip().lower()
    payload = {}
    if titulo:
        payload["titulo"] = titulo
    if descripcion:
        payload["descripcion"] = descripcion
    if completada == "s":
        payload["completada"] = True
    elif completada == "n":
        payload["completada"] = False
    headers = {"Authorization": f"Bearer {TOKEN}"}
    r = requests.put(f"{API_BASE}/api/tareas/{tarea_id}", headers=headers, json=payload)
    print(r.status_code, r.json())

def borrar_tarea():
    if not TOKEN:
        print("Hacé login primero.")
        return
    tarea_id = input("ID de tarea a borrar: ").strip()
    headers = {"Authorization": f"Bearer {TOKEN}"}
    r = requests.delete(f"{API_BASE}/api/tareas/{tarea_id}", headers=headers)
    print(r.status_code, r.json())

def menu():
    print("""
1) Registrar usuario
2) Login
3) Listar tareas
4) Crear tarea
5) Actualizar tarea
6) Borrar tarea
0) Salir
""")
    while True:
        opt = input("Opción: ").strip()
        if opt == "1":
            register()
        elif opt == "2":
            login()
        elif opt == "3":
            list_tareas()
        elif opt == "4":
            crear_tarea()
        elif opt == "5":
            actualizar_tarea()
        elif opt == "6":
            borrar_tarea()
        elif opt == "0":
            sys.exit(0)
        else:
            print("Opción inválida")

if __name__ == "__main__":
    menu()
