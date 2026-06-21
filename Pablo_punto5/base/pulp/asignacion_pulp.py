import pandas as pd
import re
import pulp
import time
import os

# =============================================================================
# DICCIONARIO DE CORRECCIÓN ORTOGRÁFICA (ARSAT CSV -> Estándar de Red)
# =============================================================================
DICCIONARIO_NOMBRES = {
    "San Miguel de Tucumán": "San Miguel de Tucuman",
    "San Miguel de Tucuman": "San Miguel de Tucuman",
    "Tucuman": "San Miguel de Tucuman",
    "Media Agua": "Villa Media Agua",
    "Villa Media Agua": "Villa Media Agua",
    "Tulumaya": "Villa Tulumaya",
    "Villa Tulumaya": "Villa Tulumaya",
    "Jujuy": "San Salvador de Jujuy",
    "San Salvador de Jujuy": "San Salvador de Jujuy",
    "Saenz Peña": "Presidencia Roque Saenz Peña",
    "Presidencia Roque Saenz Peña": "Presidencia Roque Saenz Peña",
    "San Pedro": "San Pedro BsAs",
    "San Pedro BsAs": "San Pedro BsAs",
    "San Martin": "Lib Gral San Martin",
    "Lib Gral San Martin": "Lib Gral San Martin",
    "Juan Page": "Cap Juan Page",
    "Cap Juan Page": "Cap Juan Page",
    "Santa Rosa": "Santa Rosa (LP)",
    "Santa Rosa (LP)": "Santa Rosa (LP)",
    "Gral. Alvear": "General Alvear",
    "General Alvear": "General Alvear",
    "San Nicolas": "San Nicolas de los Arroyos",
    "San Nicolas de los Arroyos": "San Nicolas de los Arroyos",
    "Paso de los Libres": "Paso de Los Libres",
    "Pehuajó": "Pehuajo"
}

def normalizar_ciudad(nombre_ciudad):
    nombre_limpio = nombre_ciudad.strip()
    nombre_limpio = re.sub(r'^roadm\s+', '', nombre_limpio)
    nombre_corregido = DICCIONARIO_NOMBRES.get(nombre_limpio, nombre_limpio)
    return f"roadm {nombre_corregido}"

def extraer_pares_nodo_a_nodo(ruta_str):
    """Desglosa la columna Ruta en una secuencia orientada de enlaces nodo a nodo"""
    ciudades = [c.strip() for c in re.split(r'\s*-\s*|\s*→\s*', ruta_str) if c.strip()]
    nodos_roadm = [normalizar_ciudad(ciudad) for ciudad in ciudades]
    
    pares = []
    for i in range(len(nodos_roadm) - 1):
        pares.append((nodos_roadm[i], nodos_roadm[i+1]))
    return pares


# =============================================================================
# PROGRAMA PRINCIPAL DE OPTIMIZACIÓN EXACTA MILP
# =============================================================================
if __name__ == "__main__":
    print("Cargando matriz de tráfico base de ARSAT...")
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    # Subir 3 niveles desde Pablo_punto5/base/pulp/ para encontrar el CSV en la raíz
    csv_path = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..', 'Demanda_Base - Tráfico base.csv'))
    
    df_demandas = pd.read_csv(csv_path)

    # 1. Crear el problema de optimización en PuLP
    prob = pulp.LpProblem("Elastic_Optical_Network_SA", pulp.LpMinimize)

    # Estructurar la lista de demandas para el modelo lineal
    demandas_modelo = []
    enlaces_totales_red = set()

    for idx, fila in df_demandas.iterrows():
        origen_norm = normalizar_ciudad(fila['Origen'])
        destino_norm = normalizar_ciudad(fila['Destino'])
        velocidad = fila['Velocidad [Gbps]']
        cantidad = int(fila['Cantidad de Enlaces'])
        enlaces_ruta = extraer_pares_nodo_a_nodo(fila['Ruta'])
        
        for e in enlaces_ruta:
            enlaces_totales_red.add(e)
            enlaces_totales_red.add((e[1], e[0])) # Guardar bidireccional

        slots_necesarios = 4 if velocidad in [100, 200] else 6

        for i in range(1, cantidad + 1):
            id_demanda = f"{origen_norm}-{destino_norm}_{velocidad}G_{i}_id{idx}"
            
            demandas_modelo.append({
                "id": id_demanda,
                "label_csv": f"{origen_norm}-{destino_norm}_{velocidad}G_{i}",
                "slots": slots_necesarios,
                "enlaces": set(enlaces_ruta)
            })

    # 2. Declaración de Variables de Decisión en PuLP
    # s[d] -> Slot inicial de la demanda (entero entre 0 y 304)
    s = pulp.LpVariable.dicts("slot_inicio", [d["id"] for d in demandas_modelo], 
                              lowBound=0, upBound=304, cat=pulp.LpInteger)
    
    # S_max -> El slot más alto utilizado en toda la red (función objetivo)
    S_max = pulp.LpVariable("S_max", lowBound=0, upBound=304, cat=pulp.LpInteger)

    # x[d1, d2] -> Variable binaria para evitar solapamiento espectral entre demandas que chocan
    x = {}
    num_dem = len(demandas_modelo)
    for i in range(num_dem):
        for j in range(i + 1, num_dem):
            d1 = demandas_modelo[i]
            d2 = demandas_modelo[j]
            
            # Condición clave: ¿Comparten algún tramo físico en común?
            # Evaluamos la intersección de tramos direccionados
            if d1["enlaces"].intersection(d2["enlaces"]):
                x[(d1["id"], d2["id"])] = pulp.LpVariable(f"overlap_{d1['id']}_{d2['id']}", cat=pulp.LpBinary)

    # 3. Definición de la Función Objetivo
    prob += S_max, "Minimizar_Slot_Maximo"

    # 4. Establecer las Restricciones del Modelo Matemático
    # M = 304 + 10 para corregir el bug original de M=304
    M = 314 
    
    for d in demandas_modelo:
        # El bloque asignado no puede superar el límite superior S_max
        prob += s[d["id"]] + d["slots"] <= S_max

    # Añadir restricciones de no-solapamiento espectral en tramos compartidos
    for (id_d1, id_d2), var_binaria in x.items():
        d1 = next(item for item in demandas_modelo if item["id"] == id_d1)
        d2 = next(item for item in demandas_modelo if item["id"] == id_d2)
        
        # Si var_binaria es 1, d1 va antes que d2. Si es 0, d2 va antes que d1.
        prob += s[d1["id"]] + d1["slots"] <= s[d2["id"]] + M * (1 - var_binaria)
        prob += s[d2["id"]] + d2["slots"] <= s[d1["id"]] + M * var_binaria

    # 5. Resolver el Modelo Matemático Lineal
    print("Enviando el modelo global al optimizador MILP (PuLP-CBC)...")
    start_time = time.time()
    
    status = prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=120))
    execution_time = time.time() - start_time

    print("\n=== REPORTE OPTIMIZACIÓN MATEMÁTICA: MILP ===")
    print(f"Estado del Optimizador: {pulp.LpStatus[status]}")
    print(f"Tiempo de cómputo: {execution_time:.4f} segundos")
    
    print(f"Filas CSV (demandas únicas): {len(df_demandas)}")
    print(f"Total Lightpaths en modelo (expandido por Cantidad de Enlaces): {len(demandas_modelo)}")
    
    if pulp.LpStatus[status] == "Optimal":
        print(f"Slot máximo óptimo alcanzado en la red (S_max): {int(pulp.value(S_max))}")
        prob_bloqueo = 0.0
    else:
        print("El optimizador no alcanzó solución óptima en el tiempo límite (120s). Demandas sin asignar se consideran bloqueadas.")
        prob_bloqueo = 100.0
    print(f"Probabilidad de Bloqueo: {prob_bloqueo:.2f}%")

    # =============================================================================
    # 6. TRANSFERENCIA DE RESULTADOS A LA MATRIZ ACUMULATIVA UNIFICADA CSV
    # =============================================================================
    matriz_espectro_final = {enlace: [""] * 304 for enlace in enlaces_totales_red}

    if pulp.LpStatus[status] == "Optimal":
        for d in demandas_modelo:
            slot_inicial_optimo = int(pulp.value(s[d["id"]]))
            for enlace in d["enlaces"]:
                for k in range(slot_inicial_optimo, slot_inicial_optimo + d["slots"]):
                    matriz_espectro_final[enlace][k] = d["label_csv"]

    # Exportación final al archivo CSV sin repetir filas de enlaces
    filas_csv = []
    for (origen, destino), slots in sorted(matriz_espectro_final.items()):
        registro = {
            "Nodo_Origen": origen,
            "Nodo_Destino": destino
        }
        for i in range(304):
            registro[f"Slot_{i+1}"] = slots[i]
        filas_csv.append(registro)

    df_salida_milp = pd.DataFrame(filas_csv)
    output_path = os.path.abspath(os.path.join(SCRIPT_DIR, 'ocupacion_base_milp.csv'))
    df_salida_milp.to_csv(output_path, index=False)
    print(f"\n Matriz única óptima global exportada con éxito: '{output_path}'")
