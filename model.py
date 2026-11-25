#!/usr/bin/env python3
import csv
import json

import pydgraph

def set_schema(client):
    # Schema basado en el modelo de Dgraph Lab 1 (deteccion de lavado de dinero)
    schema = """
    type Persona {
        id_cliente
        nombre
        score_riesgo
        pep
        TITULAR_DE
        REPRESENTANTE_DE
        UTILIZA
        ASOCIADO_CON
    }

    type Empresa {
        rfc_id
        razon_social
        fecha_constitucion
        es_fachada
        CUENTA_CORP
        RADICA_EN
    }

    type Cuenta {
        num_cuenta
        saldo
        estado_activa
        fecha_apertura
        ORIGEN
    }

    type Dispositivo {
        mac_address
        ip_frecuente
        tipo_os
        GEOLOCALIZADO_EN
    }

    type Transaccion {
        id_tx
        monto
        fecha_hora
        divisa
        DESTINO
        AUTORIZADA_EN
    }

    type Ubicacion {
        ip_origen
        pais
        ciudad
        codigo_postal
        coordenadas
    }

    # --- Persona ---
    id_cliente: string @index(exact) .
    nombre: string @index(term) .
    score_riesgo: int @index(int) .
    pep: bool .

    # --- Empresa ---
    rfc_id: string @index(exact) .
    razon_social: string @index(term) .
    fecha_constitucion: datetime .
    es_fachada: bool .

    # --- Cuenta ---
    num_cuenta: string @index(exact) .
    saldo: float @index(float) .
    estado_activa: bool @index(bool) .
    fecha_apertura: datetime .

    # --- Dispositivo ---
    mac_address: string @index(exact) .
    ip_frecuente: string .
    tipo_os: string @index(exact) .

    # --- Transaccion ---
    id_tx: string @index(exact) .
    monto: float @index(float) .
    fecha_hora: datetime .
    divisa: string @index(exact) .

    # --- Ubicacion ---
    ip_origen: string .
    pais: string @index(exact) .
    ciudad: string @index(term) .
    codigo_postal: string .
    coordenadas: geo @index(geo) .

    # --- Relaciones ---
    TITULAR_DE: [uid] @reverse .
    REPRESENTANTE_DE: [uid] .
    CUENTA_CORP: [uid] @reverse .
    ORIGEN: [uid] @reverse .
    DESTINO: [uid] .
    UTILIZA: [uid] .
    AUTORIZADA_EN: [uid] .
    RADICA_EN: [uid] .
    GEOLOCALIZADO_EN: [uid] .
    ASOCIADO_CON: [uid] .
    """
    return client.alter(pydgraph.Operation(schema=schema))

# ------------------------------------------------------------------
# CARGA DE DATOS DESDE CSV
# ------------------------------------------------------------------

def mutate_nodes(client, nodes):
    # Guarda una lista de nodos en una sola transaccion y regresa los UIDs
    # que Dgraph les asigno. Ej: {'CLI-001': '0x1', 'CLI-002': '0x2'}
    txn = client.txn()
    try:
        response = txn.mutate(set_obj=nodes)
        txn.commit()
    finally:
        txn.discard()
    return response.uids


def load_personas(client, file_path):
    personas = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            personas.append({
                'uid': '_:' + row['id_cliente'],
                'dgraph.type': 'Persona',
                'id_cliente': row['id_cliente'],
                'nombre': row['nombre'],
                'score_riesgo': int(row['score_riesgo']),
                'pep': row['pep'] == 'true',
            })
    print(f"Cargando {len(personas)} personas")
    return mutate_nodes(client, personas)


def load_empresas(client, file_path):
    empresas = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            empresas.append({
                'uid': '_:' + row['rfc_id'],
                'dgraph.type': 'Empresa',
                'rfc_id': row['rfc_id'],
                'razon_social': row['razon_social'],
                'fecha_constitucion': row['fecha_constitucion'],
                'es_fachada': row['es_fachada'] == 'true',
            })
    print(f"Cargando {len(empresas)} empresas")
    return mutate_nodes(client, empresas)


def load_cuentas(client, file_path):
    cuentas = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cuentas.append({
                'uid': '_:' + row['num_cuenta'],
                'dgraph.type': 'Cuenta',
                'num_cuenta': row['num_cuenta'],
                'saldo': float(row['saldo']),
                'estado_activa': row['estado_activa'] == 'true',
                'fecha_apertura': row['fecha_apertura'],
            })
    print(f"Cargando {len(cuentas)} cuentas")
    return mutate_nodes(client, cuentas)


def load_dispositivos(client, file_path):
    dispositivos = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            dispositivos.append({
                'uid': '_:' + row['mac_address'],
                'dgraph.type': 'Dispositivo',
                'mac_address': row['mac_address'],
                'ip_frecuente': row['ip_frecuente'],
                'tipo_os': row['tipo_os'],
            })
    print(f"Cargando {len(dispositivos)} dispositivos")
    return mutate_nodes(client, dispositivos)


def load_transacciones(client, file_path):
    transacciones = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            transacciones.append({
                'uid': '_:' + row['id_tx'],
                'dgraph.type': 'Transaccion',
                'id_tx': row['id_tx'],
                'monto': float(row['monto']),
                'fecha_hora': row['fecha_hora'],
                'divisa': row['divisa'],
            })
    print(f"Cargando {len(transacciones)} transacciones")
    return mutate_nodes(client, transacciones)


def load_ubicaciones(client, file_path):
    ubicaciones = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ubicaciones.append({
                'uid': '_:' + row['ip_origen'],
                'dgraph.type': 'Ubicacion',
                'ip_origen': row['ip_origen'],
                'pais': row['pais'],
                'ciudad': row['ciudad'],
                'codigo_postal': row['codigo_postal'],
                # Tipo geo: formato GeoJSON, el orden es [longitud, latitud]
                'coordenadas': {
                    'type': 'Point',
                    'coordinates': [float(row['longitud']), float(row['latitud'])],
                },
            })
    print(f"Cargando {len(ubicaciones)} ubicaciones")
    return mutate_nodes(client, ubicaciones)


def create_edges(client, file_path, uids):
    # Lee relaciones.csv (origen,relacion,destino) y crea cada arista
    # usando los UIDs reales que regresaron las funciones load_*
    txn = client.txn()
    try:
        total = 0
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                mutation = {
                    'uid': uids[row['origen']],
                    row['relacion']: {
                        'uid': uids[row['destino']]
                    }
                }
                txn.mutate(set_obj=mutation)
                total += 1
        txn.commit()
        print(f"Relaciones creadas: {total}")
    finally:
        txn.discard()


def create_data(client):
    # 1. Cargar nodos. Cada funcion regresa un diccionario llave -> uid
    uids = {}
    uids.update(load_personas(client, 'data/personas.csv'))
    uids.update(load_empresas(client, 'data/empresas.csv'))
    uids.update(load_cuentas(client, 'data/cuentas.csv'))
    uids.update(load_dispositivos(client, 'data/dispositivos.csv'))
    uids.update(load_transacciones(client, 'data/transacciones.csv'))
    uids.update(load_ubicaciones(client, 'data/ubicaciones.csv'))
    print(f"Nodos creados: {len(uids)}")

    # 2. Crear relaciones usando los UIDs que nos dio Dgraph
    create_edges(client, 'data/relaciones.csv', uids)


# ------------------------------------------------------------------
# QUERIES
# ------------------------------------------------------------------

def run_query(client, query, variables=None):
    # Ejecuta una query de solo lectura y regresa el resultado como diccionario
    res = client.txn(read_only=True).query(query, variables=variables)
    return json.loads(res.json)


def print_result(titulo, data):
    print(f"\n--- {titulo} ---")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def search_persona_nombre(client, nombre):
    # Indice de TEXTO: nombre @index(term)
    # anyofterms encuentra a quien tenga cualquiera de las palabras buscadas
    query = """query search_persona($nombre: string) {
        personas(func: anyofterms(nombre, $nombre)) {
            id_cliente
            nombre
            score_riesgo
            pep
        }
    }"""
    variables = {'$nombre': nombre}
    data = run_query(client, query, variables)
    print_result(f"Personas con '{nombre}' en el nombre: {len(data['personas'])}", data)


def search_score_riesgo(client, minimo):
    # Indice NUMERICO: score_riesgo @index(int)
    # ge = greater or equal (mayor o igual)
    query = """query score_riesgo($minimo: int) {
        personas(func: ge(score_riesgo, $minimo)) {
            nombre
            score_riesgo
            pep
        }
    }"""
    variables = {'$minimo': str(minimo)}
    data = run_query(client, query, variables)
    print_result(f"Personas con score de riesgo >= {minimo}", data)


def red_de_persona(client, id_cliente):
    # Query de GRAFO con varios tipos de nodo:
    # Persona -> Cuenta -> Transaccion -> Cuenta destino / Dispositivo
    query = """query red_persona($id: string) {
        persona(func: eq(id_cliente, $id)) {
            nombre
            score_riesgo
            TITULAR_DE {
                num_cuenta
                saldo
                ORIGEN {
                    id_tx
                    monto
                    divisa
                    DESTINO {
                        num_cuenta
                    }
                    AUTORIZADA_EN {
                        mac_address
                        tipo_os
                    }
                }
            }
            REPRESENTANTE_DE {
                razon_social
                es_fachada
            }
        }
    }"""
    variables = {'$id': id_cliente}
    data = run_query(client, query, variables)
    print_result(f"Red de la persona {id_cliente}", data)


def titular_de_cuenta(client, num_cuenta):
    # Relacion en REVERSA: TITULAR_DE va de Persona -> Cuenta.
    # Con ~TITULAR_DE vamos de la Cuenta -> Persona (gracias a @reverse)
    query = """query titular($num: string) {
        cuenta(func: eq(num_cuenta, $num)) {
            num_cuenta
            saldo
            estado_activa
            titular: ~TITULAR_DE {
                nombre
                score_riesgo
            }
        }
    }"""
    variables = {'$num': num_cuenta}
    data = run_query(client, query, variables)
    print_result(f"Titular de la cuenta {num_cuenta}", data)


def transacciones_ordenadas(client):
    # ORDENAR: orderdesc ordena de mayor a menor monto (necesita indice en monto)
    # Tambien usamos ~ORIGEN (reversa) para saber de que cuenta salio el dinero
    query = """{
        transacciones(func: type(Transaccion), orderdesc: monto) {
            id_tx
            monto
            divisa
            origen: ~ORIGEN {
                num_cuenta
            }
            DESTINO {
                num_cuenta
            }
        }
    }"""
    data = run_query(client, query)
    print_result("Transacciones ordenadas por monto (mayor a menor)", data)


def contar_cuentas(client):
    # COUNT: count(TITULAR_DE) cuenta las aristas de cada persona
    # count(uid) cuenta cuantos nodos regreso la funcion
    query = """{
        total_personas(func: type(Persona)) {
            total: count(uid)
        }
        personas(func: type(Persona), orderasc: nombre) {
            nombre
            num_cuentas: count(TITULAR_DE)
        }
    }"""
    data = run_query(client, query)
    print_result("Numero de cuentas por persona", data)


def transacciones_paginadas(client, pagina, por_pagina):
    # PAGINACION: first = cuantos resultados, offset = cuantos saltar
    # Pagina 1 -> offset 0, pagina 2 -> offset 3, etc.
    offset = (pagina - 1) * por_pagina
    query = """query paginacion($first: int, $offset: int) {
        transacciones(func: type(Transaccion), orderasc: id_tx, first: $first, offset: $offset) {
            id_tx
            monto
            divisa
            fecha_hora
        }
    }"""
    variables = {'$first': str(por_pagina), '$offset': str(offset)}
    data = run_query(client, query, variables)
    print_result(f"Transacciones - pagina {pagina} ({por_pagina} por pagina)", data)


def ubicaciones_cercanas(client, latitud, longitud, km):
    # Tipo GEO: near(predicado, [longitud, latitud], distancia_en_metros)
    metros = int(km * 1000)
    query = f"""{{
        ubicaciones(func: near(coordenadas, [{longitud}, {latitud}], {metros})) {{
            ciudad
            pais
            ip_origen
            coordenadas
        }}
    }}"""
    data = run_query(client, query)
    print_result(f"Ubicaciones a menos de {km} km de ({latitud}, {longitud})", data)


# ------------------------------------------------------------------
# DELETES
# ------------------------------------------------------------------

def delete_cuentas_inactivas(client):
    # DELETE CON CONDICION: borra las cuentas con estado_activa = false.
    # 1. Buscamos los uids de las cuentas que cumplen la condicion y,
    #    con las reversas, quien apunta a ellas (persona o empresa).
    query = """{
        cuentas(func: eq(estado_activa, false)) {
            uid
            num_cuenta
            titular: ~TITULAR_DE {
                uid
            }
            empresa: ~CUENTA_CORP {
                uid
            }
        }
    }"""
    data = run_query(client, query)

    if len(data['cuentas']) == 0:
        print("No hay cuentas inactivas para borrar")
        return

    # 2. Borramos en una sola transaccion
    txn = client.txn()
    try:
        for cuenta in data['cuentas']:
            # Quitar la arista Persona -TITULAR_DE-> Cuenta
            for persona in cuenta.get('titular', []):
                txn.mutate(del_obj={'uid': persona['uid'], 'TITULAR_DE': {'uid': cuenta['uid']}})
            # Quitar la arista Empresa -CUENTA_CORP-> Cuenta
            for empresa in cuenta.get('empresa', []):
                txn.mutate(del_obj={'uid': empresa['uid'], 'CUENTA_CORP': {'uid': cuenta['uid']}})
            # Borrar el nodo Cuenta (todos sus predicados)
            txn.mutate(del_obj={'uid': cuenta['uid']})
            print(f"Cuenta {cuenta['num_cuenta']} eliminada")
        txn.commit()
        print(f"Total de cuentas inactivas eliminadas: {len(data['cuentas'])}")
    finally:
        txn.discard()


def drop_all(client):
    # DELETE ALL: borra todos los datos Y el schema del grafo
    return client.alter(pydgraph.Operation(drop_all=True))
