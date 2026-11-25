#!/usr/bin/env python3
import os

import pydgraph

import model

DGRAPH_URI = os.getenv('DGRAPH_URI', 'localhost:9080')

def print_menu():
    mm_options = {
        1: "Cargar datos desde CSV",
        2: "Buscar persona por nombre        (indice de texto)",
        3: "Personas por score de riesgo     (indice numerico)",
        4: "Red de una persona               (varios tipos de nodo)",
        5: "Titular de una cuenta            (relacion en reversa)",
        6: "Transacciones por monto          (ordenar)",
        7: "Cuentas por persona              (count)",
        8: "Transacciones por pagina         (paginacion)",
        9: "Ubicaciones cercanas             (geo)",
        10: "Borrar cuentas inactivas         (delete con condicion)",
        11: "Borrar todo el grafo             (drop all)",
        0: "Salir",
    }
    print("\n===== Deteccion de fraude - Dgraph =====")
    for key in mm_options.keys():
        print(key, '--', mm_options[key])


# Conexión directa con el servidor Dgraph usando gRPC.
def create_client_stub():
    return pydgraph.DgraphClientStub(DGRAPH_URI)

# Crea el cliente principal de Dgraph: realizar operaciones de alto nivel como queries, mutaciones y transacciones.
def create_client(client_stub):
    return pydgraph.DgraphClient(client_stub)

def close_client_stub(client_stub):
    client_stub.close()

def main():
    # Inicializar Client Stub y Dgraph Client
    client_stub = create_client_stub()
    client = create_client(client_stub)

    # Crear schema
    model.set_schema(client)
    print(f"Conectado a Dgraph en {DGRAPH_URI}. Schema creado.")

    while(True):
        print_menu()
        try:
            option = int(input('Elige una opcion: '))
        except ValueError:
            print("Opcion invalida, escribe un numero del menu")
            continue

        # Si una opcion falla, mostramos el error y regresamos al menu
        try:
            if option == 1:
                model.create_data(client)
            elif option == 2:
                nombre = input("Nombre o palabra a buscar: ")
                model.search_persona_nombre(client, nombre)
            elif option == 3:
                minimo = int(input("Score de riesgo minimo (0-100): "))
                model.search_score_riesgo(client, minimo)
            elif option == 4:
                id_cliente = input("ID del cliente (ej. CLI-001): ")
                model.red_de_persona(client, id_cliente)
            elif option == 5:
                num_cuenta = input("Numero de cuenta (ej. CTA-1111): ")
                model.titular_de_cuenta(client, num_cuenta)
            elif option == 6:
                model.transacciones_ordenadas(client)
            elif option == 7:
                model.contar_cuentas(client)
            elif option == 8:
                pagina = int(input("Numero de pagina: "))
                por_pagina = int(input("Resultados por pagina: "))
                model.transacciones_paginadas(client, pagina, por_pagina)
            elif option == 9:
                latitud = float(input("Latitud (ej. 20.6597): "))
                longitud = float(input("Longitud (ej. -103.3496): "))
                km = float(input("Radio en km: "))
                model.ubicaciones_cercanas(client, latitud, longitud, km)
            elif option == 10:
                model.delete_cuentas_inactivas(client)
            elif option == 11:
                confirmar = input("Se borraran TODOS los datos. Continuar? (s/n): ")
                if confirmar == 's':
                    model.drop_all(client)
                    # drop_all tambien borra el schema, lo volvemos a crear
                    model.set_schema(client)
                    print("Grafo borrado. Schema creado de nuevo.")
            elif option == 0:
                close_client_stub(client_stub)
                print("Adios")
                exit(0)
            else:
                print("Opcion invalida, escribe un numero del menu")
        except ValueError:
            print("Dato invalido: se esperaba un numero")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error: {}'.format(e))
