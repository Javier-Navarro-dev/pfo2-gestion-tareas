"""Cliente de consola para la API de tareas."""
import requests

BASE = "http://127.0.0.1:5000"
s = requests.Session()  # mantiene la cookie de sesión tras el login


def pedir_credenciales():
    return {"usuario": input("Usuario: ").strip(), "contraseña": input("Contraseña: ")}


def mostrar(r):
    try:
        print(f"[{r.status_code}]", r.json())
    except ValueError:
        print(f"[{r.status_code}]\n{r.text}")


def main():
    while True:
        print("\n1) Registrarse  2) Iniciar sesión  3) Ver tareas  4) Salir")
        op = input("Opción: ").strip()
        try:
            if op == "1":
                mostrar(s.post(f"{BASE}/registro", json=pedir_credenciales()))
            elif op == "2":
                mostrar(s.post(f"{BASE}/login", json=pedir_credenciales()))
            elif op == "3":
                mostrar(s.get(f"{BASE}/tareas"))
            elif op == "4":
                break
            else:
                print("Opción inválida")
        except requests.ConnectionError:
            print("No se pudo conectar. ¿Está corriendo servidor.py?")


if __name__ == "__main__":
    main()
