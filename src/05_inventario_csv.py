"""
05_inventario_csv.py - Script propio del grupo (TP4 Redes 3643)

Que hace:
  1. Pide el ticket al Network Controller de Packet Tracer (POST /ticket).
  2. Trae los dispositivos de red (GET /network-device) y los hosts (GET /host).
  3. Muestra un resumen en pantalla y guarda todo en un archivo CSV
     (inventario_red.csv) que se puede abrir con Excel.

Que le agrega a los scripts de la catedra:
  - No hay que copiar el ticket a mano: lo pide solo.
  - La clave no queda escrita en el codigo (el repositorio es publico).
  - Junta equipos y hosts en un unico inventario exportado a archivo.

Requisitos: Packet Tracer abierto, acceso externo habilitado (puerto 58000)
y la biblioteca requests (pip install -r requirements.txt).
"""

import csv
import getpass
from datetime import datetime

import requests

BASE_URL = "http://localhost:58000/api/v1"
ARCHIVO_CSV = "inventario_red.csv"


def pedir_ticket(usuario, clave):
    """Devuelve el serviceTicket del Network Controller."""
    resp = requests.post(
        BASE_URL + "/ticket",
        json={"username": usuario, "password": clave},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    print("POST /ticket ->", resp.status_code)
    resp.raise_for_status()
    return resp.json()["response"]["serviceTicket"]


def consultar(endpoint, ticket):
    """Hace un GET al endpoint y devuelve la lista 'response'."""
    resp = requests.get(
        BASE_URL + endpoint,
        headers={"X-Auth-Token": ticket},
        timeout=10,
    )
    print("GET", endpoint, "->", resp.status_code)
    resp.raise_for_status()
    return resp.json().get("response", [])


def main():
    print("=== Inventario de la red (Network Controller) ===")
    usuario = input("Usuario del NC [cisco]: ").strip() or "cisco"
    clave = getpass.getpass("Clave del NC: ")

    try:
        ticket = pedir_ticket(usuario, clave)
    except requests.exceptions.ConnectionError:
        print("No se pudo conectar. Revisen que Packet Tracer este abierto "
              "y que el acceso externo al NC este habilitado.")
        return
    except requests.exceptions.HTTPError:
        print("El NC rechazo el pedido del ticket. Revisen usuario y clave.")
        return

    dispositivos = consultar("/network-device", ticket)
    hosts = consultar("/host", ticket)

    filas = []
    for d in dispositivos:
        filas.append({
            "categoria": "Dispositivo de red",
            "nombre": d.get("hostname", ""),
            "ip": d.get("managementIpAddress", ""),
            "modelo_o_tipo": d.get("platformId", ""),
            "serie_o_mac": d.get("serialNumber", ""),
            "software_o_interfaz": d.get("softwareVersion", ""),
        })
    for h in hosts:
        filas.append({
            "categoria": "Host",
            "nombre": h.get("hostName", ""),
            "ip": h.get("hostIp", ""),
            "modelo_o_tipo": h.get("hostType", ""),
            "serie_o_mac": h.get("hostMac", ""),
            "software_o_interfaz": h.get("connectedInterfaceName", ""),
        })

    columnas = ["categoria", "nombre", "ip", "modelo_o_tipo",
                "serie_o_mac", "software_o_interfaz"]
    with open(ARCHIVO_CSV, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas, delimiter=";")
        escritor.writeheader()
        escritor.writerows(filas)

    print()
    print(f"{'CATEGORIA':<20}{'NOMBRE':<18}{'IP':<18}{'MODELO/TIPO'}")
    for fila in filas:
        print(f"{fila['categoria']:<20}{fila['nombre']:<18}"
              f"{fila['ip']:<18}{fila['modelo_o_tipo']}")
    print()
    print(f"Dispositivos de red: {len(dispositivos)}  |  Hosts: {len(hosts)}")
    print(f"Archivo generado: {ARCHIVO_CSV} "
          f"({datetime.now().strftime('%d/%m/%Y %H:%M')})")


if __name__ == "__main__":
    main()
