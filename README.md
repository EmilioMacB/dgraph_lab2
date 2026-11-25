# Dgraph Lab 2 - Pydgraph: Detección de fraude bancario

Aplicación de consola en Python (pydgraph) basada en el modelo de datos de **Dgraph Lab 1**
(red de lavado de dinero). Basada en el repositorio
[iteso-bdnr-dgraph-p2025](https://github.com/anmolpathry12/iteso-bdnr-dgraph-p2025).

## Estructura

```
main.py      -> Cliente: conexión, creación del schema y menú
model.py     -> Modelo: schema, carga de CSV, queries y deletes
data/        -> CSVs con los datos
  personas.csv, empresas.csv, cuentas.csv,
  dispositivos.csv, transacciones.csv, ubicaciones.csv  (nodos)
  relaciones.csv                                         (aristas: origen,relacion,destino)
```

## Modelo

**Tipos de nodo (6):** Persona, Empresa, Cuenta, Dispositivo, Transaccion, Ubicacion

**Relaciones (10):** TITULAR_DE, REPRESENTANTE_DE, CUENTA_CORP, ORIGEN, DESTINO,
UTILIZA, AUTORIZADA_EN, RADICA_EN, GEOLOCALIZADO_EN, ASOCIADO_CON

| Requisito | Dónde |
|---|---|
| Índice de texto | `nombre: string @index(term)` |
| Índice numérico | `score_riesgo: int @index(int)`, `monto: float @index(float)` |
| Tipo geo | `coordenadas: geo @index(geo)` en Ubicacion |
| Relación en reversa | `TITULAR_DE`, `ORIGEN`, `CUENTA_CORP` con `@reverse` |

## Cómo ejecutar

### 1. Levantar Dgraph
```
docker run --name dgraph-lab2 -d -p 8081:8080 -p 9081:9080 dgraph/standalone
```
> Usamos los puertos 8081/9081 para no chocar con otra instancia de Dgraph.
> Si usas los puertos por defecto (8080/9080) no necesitas `DGRAPH_URI`.

### 2. Crear el entorno virtual e instalar dependencias
```
# Linux/MacOS
python3 -m venv ./venv
source ./venv/bin/activate

# Windows
python3 -m venv ./venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 3. Ejecutar el cliente (desde la carpeta del proyecto)
```
DGRAPH_URI=localhost:9081 python3 main.py
```
Al iniciar, el cliente se conecta y crea el schema automáticamente.

## Menú

| Opción | Acción |
|---|---|
| 1 | Cargar datos desde CSV (ejecutar una sola vez; para recargar usar antes la opción 11) |
| 2 | Buscar persona por nombre (índice de texto, `anyofterms`) |
| 3 | Personas por score de riesgo mínimo (índice numérico, `ge`) |
| 4 | Red de una persona: Persona → Cuenta → Transacción → Cuenta/Dispositivo (varios tipos) |
| 5 | Titular de una cuenta (reversa `~TITULAR_DE`) |
| 6 | Transacciones ordenadas por monto (`orderdesc`) |
| 7 | Cuentas por persona (`count`) |
| 8 | Transacciones por página (`first` / `offset`) |
| 9 | Ubicaciones cercanas a un punto (geo, `near`) |
| 10 | Borrar cuentas inactivas (delete con condición `estado_activa = false`) |
| 11 | Borrar todo el grafo (`drop_all`) y recrear el schema |
| 0 | Salir |

### Valores de ejemplo para probar
- Opción 2: `Juan`
- Opción 3: `60`
- Opción 4: `CLI-004`
- Opción 5: `CTA-5555`
- Opción 8: página `2`, `3` por página
- Opción 9: `20.6597`, `-103.3496`, `20` km (Guadalajara)
