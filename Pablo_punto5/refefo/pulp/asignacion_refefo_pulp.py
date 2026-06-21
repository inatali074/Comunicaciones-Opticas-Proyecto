"""
Asignación de demandas REFEFO sobre la red base con MILP (PuLP-CBC).

Flujo:
  1. Carga la matriz espectral base desde 'ocupacion_base_milp_test.csv'.
  2. Lee las demandas REFEFO desde 'demandas_refefo.csv'.
  3. Pre-selecciona el path para cada demanda (factibles primero, sino todos).
  4. Formula un MILP donde:
     - Variables: slot de inicio s[d] para cada demanda refefo
     - Restricciones: no pisar slots de la base, no solaparse entre refefo
     - Objetivo: minimizar S_max (slot máximo utilizado)
  5. Exporta la matriz espectral final y un reporte de estadísticas.
"""

import pandas as pd
import re
import pulp
import time
import os

# Estructura: script está en refefo/pulp/
# REFEFO_DIR → refefo/       (un nivel arriba del script)
# PUNTO5_DIR → Pablo_punto5/ (dos niveles arriba del script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REFEFO_DIR = os.path.dirname(SCRIPT_DIR)
PUNTO5_DIR = os.path.dirname(REFEFO_DIR)

BASE_OCCUPATION_CSV = os.path.abspath(os.path.join(PUNTO5_DIR, "base", "pulp", "ocupacion_base_milp.csv"))
DEMANDAS_REFEFO_CSV = os.path.join(REFEFO_DIR, "demandas_refefo.csv")
OUTPUT_OCCUPATION_CSV = os.path.join(SCRIPT_DIR, "ocupacion_refefo_pulp.csv")
OUTPUT_REPORT_TXT = os.path.join(SCRIPT_DIR, "reporte_refefo_pulp.txt")

TOTAL_SLOTS = 304
M_BIG = 310  # Big-M (> 304, corrige el bug del original que usaba M=304)
TIME_LIMIT = 120
GAP_REL = 0.05


# =============================================================================
# NORMALIZACIÓN (idéntica al original)
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
    "Pehuajó": "Pehuajo",
}

def normalizar_ciudad(nombre_ciudad):
    nombre_limpio = nombre_ciudad.strip()
    nombre_limpio = re.sub(r'^roadm\s+', '', nombre_limpio)
    nombre_corregido = DICCIONARIO_NOMBRES.get(nombre_limpio, nombre_limpio)
    return f"roadm {nombre_corregido}"

def extraer_pares_nodo_a_nodo(ruta_str):
    ciudades = [c.strip() for c in re.split(r'\s*-\s*|\s*→\s*', ruta_str) if c.strip()]
    nodos_roadm = [normalizar_ciudad(ciudad) for ciudad in ciudades]
    pares = []
    for i in range(len(nodos_roadm) - 1):
        pares.append((nodos_roadm[i], nodos_roadm[i + 1]))
    return pares

def calcular_slots(gbps):
    if gbps in [100, 200, 100.0, 200.0]:
        return 4
    else:
        return 6


# =============================================================================
# CARGA DE RED BASE
# =============================================================================
def cargar_base(csv_path):
    """Carga la ocupación base como dict {(origen,destino): [304 strings]}."""
    print(f"  Cargando estado base desde: {csv_path}")
    df = pd.read_csv(csv_path)
    espectro = {}
    for _, fila in df.iterrows():
        par = (fila["Nodo_Origen"], fila["Nodo_Destino"])
        slots = []
        for i in range(1, 305):
            val = fila[f"Slot_{i}"]
            slots.append("" if pd.isna(val) else str(val))
        espectro[par] = slots

    n_enlaces = len(espectro)
    s_ocu = sum(1 for sl in espectro.values() for s in sl if s != "")
    s_max = 0
    for sl in espectro.values():
        for i, s in enumerate(sl):
            if s != "" and (i + 1) > s_max:
                s_max = i + 1
    print(f"  → {n_enlaces} enlaces, {s_ocu} slots ocupados, S_max base = {s_max}")
    return espectro, s_max


# =============================================================================
# CÁLCULO DE POSICIONES VÁLIDAS (considerando base)
# =============================================================================
def calcular_posiciones_validas(enlaces, slots_necesarios, base_espectro):
    """
    Calcula las posiciones de inicio válidas para una demanda,
    considerando la ocupación base. Una posición p es válida si
    el bloque [p, p+slots-1] está libre en TODOS los enlaces de la ruta.
    """
    max_start = TOTAL_SLOTS - slots_necesarios
    validas = set(range(max_start + 1))

    for enlace in enlaces:
        if enlace not in base_espectro:
            continue  # Enlace no existe en la base = todo libre
        slots_enlace = base_espectro[enlace]
        for k in range(TOTAL_SLOTS):
            if slots_enlace[k] != "":
                # Slot k ocupado → prohibir starts que lo incluyan
                for p in range(max(0, k - slots_necesarios + 1), min(k + 1, max_start + 1)):
                    validas.discard(p)

    return sorted(validas)


def agrupar_en_rangos(posiciones_prohibidas, max_start):
    """Agrupa posiciones prohibidas contiguas en rangos [a,b]."""
    if not posiciones_prohibidas:
        return []
    sorted_p = sorted(posiciones_prohibidas)
    rangos = []
    start = sorted_p[0]
    end = sorted_p[0]
    for p in sorted_p[1:]:
        if p == end + 1:
            end = p
        else:
            rangos.append((start, end))
            start = p
            end = p
    rangos.append((start, end))
    return rangos


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================
def main():
    print("=" * 70)
    print("  ASIGNACIÓN DE DEMANDAS REFEFO CON MILP (PuLP-CBC)")
    print("  Sobre estado base: ocupacion_base_milp.csv (con fix Cantidad de Enlaces)")
    print("=" * 70)

    # 1. Cargar base
    base_espectro, base_s_max = cargar_base(BASE_OCCUPATION_CSV)
    base_slots_ocupados = sum(1 for sl in base_espectro.values() for s in sl if s != "")
    base_total_slots = len(base_espectro) * TOTAL_SLOTS

    # 2. Cargar demandas REFEFO y seleccionar paths
    print(f"\n  Cargando demandas REFEFO desde: {DEMANDAS_REFEFO_CSV}")
    df_refefo = pd.read_csv(DEMANDAS_REFEFO_CSV)
    iteraciones = sorted(df_refefo["Iteración"].unique())
    print(f"  → {len(iteraciones)} iteraciones a procesar")

    # Pre-seleccionar path y calcular posiciones válidas para cada demanda
    demandas_milp = []
    demandas_sin_espacio = []  # Pre-bloqueadas (sin posiciones válidas)

    print("\n  Pre-procesando demandas y calculando posiciones válidas...")
    for iter_id in iteraciones:
        df_iter = df_refefo[df_refefo["Iteración"] == iter_id].sort_values("K_Path")
        source = df_iter.iloc[0]["Source"]
        destination = df_iter.iloc[0]["Destination"]
        gbps = df_iter.iloc[0]["Gbps"]
        slots_necesarios = calcular_slots(gbps)

        df_factibles = df_iter[
            (df_iter["Direct_Feasible"] == True) | (df_iter["Reg_Feasible"] == True)
        ]
        df_a_intentar = df_factibles if len(df_factibles) > 0 else df_iter
        tiene_factibles = len(df_factibles) > 0

        # Intentar cada K-path y elegir el primero con posiciones válidas
        mejor_path = None
        for _, fila in df_a_intentar.iterrows():
            enlaces = extraer_pares_nodo_a_nodo(fila["Path_Sequence"])
            pos_validas = calcular_posiciones_validas(enlaces, slots_necesarios, base_espectro)
            if pos_validas:
                mejor_path = {
                    "iter_id": iter_id,
                    "source": source,
                    "destination": destination,
                    "gbps": gbps,
                    "k_path": fila["K_Path"],
                    "slots": slots_necesarios,
                    "enlaces": set(tuple(e) for e in enlaces),
                    "enlaces_lista": enlaces,
                    "posiciones_validas": pos_validas,
                    "tiene_factibles": tiene_factibles,
                }
                break

        if mejor_path:
            origen_norm = normalizar_ciudad(source)
            destino_norm = normalizar_ciudad(destination)
            mejor_path["id"] = f"{origen_norm}-{destino_norm}_{int(gbps)}G_ref{iter_id}"
            mejor_path["label"] = f"{origen_norm}-{destino_norm}_{int(gbps)}G_ref{iter_id}"
            demandas_milp.append(mejor_path)
        else:
            demandas_sin_espacio.append({
                "iter_id": iter_id, "source": source,
                "destination": destination, "gbps": gbps,
                "tiene_factibles": tiene_factibles,
            })

    print(f"  → {len(demandas_milp)} demandas con posiciones válidas (entran al MILP)")
    print(f"  → {len(demandas_sin_espacio)} demandas pre-bloqueadas (sin espacio en base)")

    # 3. Construir el modelo MILP
    print("\n  Construyendo modelo MILP...")
    prob = pulp.LpProblem("Refefo_RSA_MILP", pulp.LpMinimize)

    # Variables: slot de inicio para cada demanda
    s = {}
    for d in demandas_milp:
        s[d["id"]] = pulp.LpVariable(
            f"s_{d['iter_id']}",
            lowBound=0,
            upBound=TOTAL_SLOTS - d["slots"],
            cat=pulp.LpInteger
        )

    # Variable objetivo: S_max
    S_max = pulp.LpVariable("S_max", lowBound=base_s_max, upBound=TOTAL_SLOTS, cat=pulp.LpInteger)
    prob += S_max, "Minimizar_Slot_Maximo"

    # Restricción: S_max >= s[d] + slots[d] para cada demanda
    for d in demandas_milp:
        prob += s[d["id"]] + d["slots"] <= S_max, f"smax_{d['iter_id']}"

    # Restricciones de base: s[d] debe estar en una posición válida
    # Convertimos a "rangos prohibidos" y usamos big-M
    print("  Agregando restricciones de ocupación base...")
    z_count = 0
    for d in demandas_milp:
        max_start = TOTAL_SLOTS - d["slots"]
        todas = set(range(max_start + 1))
        prohibidas = todas - set(d["posiciones_validas"])

        if not prohibidas:
            continue

        rangos = agrupar_en_rangos(prohibidas, max_start)
        for r_idx, (a, b) in enumerate(rangos):
            z = pulp.LpVariable(f"z_{d['iter_id']}_{r_idx}", cat=pulp.LpBinary)
            # z=0 → s[d] <= a-1;  z=1 → s[d] >= b+1
            prob += s[d["id"]] <= a - 1 + M_BIG * z, f"base_lo_{d['iter_id']}_{r_idx}"
            prob += s[d["id"]] >= b + 1 - M_BIG * (1 - z), f"base_hi_{d['iter_id']}_{r_idx}"
            z_count += 1

    print(f"  → {z_count} variables binarias para restricciones de base")

    # Restricciones de no-solapamiento entre demandas refefo que comparten enlaces
    print("  Calculando pares con enlaces compartidos...")
    x = {}
    x_count = 0
    num_dem = len(demandas_milp)
    for i in range(num_dem):
        for j in range(i + 1, num_dem):
            d1 = demandas_milp[i]
            d2 = demandas_milp[j]
            if d1["enlaces"].intersection(d2["enlaces"]):
                var_name = f"x_{d1['iter_id']}_{d2['iter_id']}"
                x_var = pulp.LpVariable(var_name, cat=pulp.LpBinary)
                x[(d1["id"], d2["id"])] = x_var

                prob += (s[d1["id"]] + d1["slots"] <= s[d2["id"]] + M_BIG * (1 - x_var),
                         f"novlp_a_{d1['iter_id']}_{d2['iter_id']}")
                prob += (s[d2["id"]] + d2["slots"] <= s[d1["id"]] + M_BIG * x_var,
                         f"novlp_b_{d1['iter_id']}_{d2['iter_id']}")
                x_count += 1

    print(f"  → {x_count} pares con solapamiento potencial")

    # Warm start: inyectar solución First-Fit como valor inicial
    print("  Inyectando warm-start (First-Fit greedy)...")
    for d in demandas_milp:
        if d["posiciones_validas"]:
            s[d["id"]].setInitialValue(d["posiciones_validas"][0])

    # 4. Resolver
    total_vars = len(demandas_milp) + 1 + z_count + x_count
    total_constraints = len(prob.constraints)
    print(f"\n  Modelo: {total_vars} variables, {total_constraints} restricciones")
    print(f"  Resolviendo con CBC (timeLimit={TIME_LIMIT}s, gapRel={GAP_REL})...")

    start_time = time.time()
    status = prob.solve(pulp.PULP_CBC_CMD(
        msg=True, timeLimit=TIME_LIMIT, gapRel=GAP_REL, warmStart=True
    ))
    execution_time = time.time() - start_time

    status_str = pulp.LpStatus[status]
    print(f"\n  Estado del solver: {status_str}")
    print(f"  Tiempo de cómputo: {execution_time:.2f} segundos")

    # 5. Extraer resultados
    s_max_val = pulp.value(S_max)
    tiene_solucion = (status_str == "Optimal")

    # Construir la matriz espectral final
    espectro_final = {}
    for par, slots in base_espectro.items():
        espectro_final[par] = list(slots)

    demandas_exitosas = 0
    demandas_bloqueadas = len(demandas_sin_espacio)
    log_detalle = []

    if tiene_solucion:
        print(f"  S_max óptimo: {int(s_max_val)}")

        for d in demandas_milp:
            slot_val = pulp.value(s[d["id"]])
            if slot_val is not None:
                slot_inicio = int(slot_val)
                demandas_exitosas += 1

                # Escribir en la matriz
                for enlace in d["enlaces_lista"]:
                    enlace_t = tuple(enlace) if not isinstance(enlace, tuple) else enlace
                    if enlace_t not in espectro_final:
                        espectro_final[enlace_t] = [""] * TOTAL_SLOTS
                    for k in range(slot_inicio, slot_inicio + d["slots"]):
                        espectro_final[enlace_t][k] = d["label"]

                tag_fact = "" if d["tiene_factibles"] else " [no-fact]"
                log_detalle.append({
                    "Iteración": d["iter_id"], "Source": d["source"],
                    "Destination": d["destination"], "Gbps": d["gbps"],
                    "Resultado": f"ASIGNADA{tag_fact}",
                    "K_Path_Asignado": d["k_path"],
                    "Slots_Asignados": d["slots"],
                    "Slot_Inicio": slot_inicio,
                })
            else:
                demandas_bloqueadas += 1
                log_detalle.append({
                    "Iteración": d["iter_id"], "Source": d["source"],
                    "Destination": d["destination"], "Gbps": d["gbps"],
                    "Resultado": "BLOQUEADA (solver)",
                    "K_Path_Asignado": "-", "Slots_Asignados": 0,
                    "Slot_Inicio": "-",
                })
    else:
        print("  ⚠ El solver no encontró solución factible.")
        demandas_bloqueadas += len(demandas_milp)
        for d in demandas_milp:
            log_detalle.append({
                "Iteración": d["iter_id"], "Source": d["source"],
                "Destination": d["destination"], "Gbps": d["gbps"],
                "Resultado": "BLOQUEADA (infactible)",
                "K_Path_Asignado": "-", "Slots_Asignados": 0,
                "Slot_Inicio": "-",
            })

    # Agregar demandas pre-bloqueadas al log
    for d in demandas_sin_espacio:
        tag = "sin paths factibles" if not d["tiene_factibles"] else "sin espacio en base"
        log_detalle.append({
            "Iteración": d["iter_id"], "Source": d["source"],
            "Destination": d["destination"], "Gbps": d["gbps"],
            "Resultado": f"BLOQUEADA ({tag})",
            "K_Path_Asignado": "-", "Slots_Asignados": 0,
            "Slot_Inicio": "-",
        })
    log_detalle.sort(key=lambda x: x["Iteración"])

    # Estadísticas finales
    total_demandas = len(iteraciones)
    final_slots_ocu = sum(1 for sl in espectro_final.values() for s in sl if s != "")
    final_total_slots = len(espectro_final) * TOTAL_SLOTS
    final_s_max = 0
    for sl in espectro_final.values():
        for i, s_val in enumerate(sl):
            if s_val != "" and (i + 1) > final_s_max:
                final_s_max = i + 1
    final_ocu_pct = (final_slots_ocu / final_total_slots * 100) if final_total_slots > 0 else 0
    prob_bloqueo = (demandas_bloqueadas / total_demandas * 100) if total_demandas > 0 else 0

    print("\n" + "=" * 70)
    print("  REPORTE FINAL")
    print("=" * 70)
    print(f"\n  Tiempo de ejecución:            {execution_time:.2f} segundos")
    print(f"  Estado del solver:              {status_str}")
    print(f"  Demandas REFEFO totales:        {total_demandas}")
    print(f"  Demandas asignadas con éxito:   {demandas_exitosas}")
    print(f"  Demandas bloqueadas:            {demandas_bloqueadas}")
    print(f"\n  Probabilidad de bloqueo:        {prob_bloqueo:.2f}%")
    print(f"\n  Estado final de la red:")
    print(f"    Enlaces: {len(espectro_final)}")
    print(f"    Slots ocupados: {final_slots_ocu} / {final_total_slots}")
    print(f"    Ocupación: {final_ocu_pct:.2f}%")
    print(f"    Slot máximo utilizado (S_max): {final_s_max}")

    delta_slots = final_slots_ocu - base_slots_ocupados
    print(f"\n  Δ Slots ocupados (refefo):      +{delta_slots}")
    print(f"  Δ S_max:                        {base_s_max} → {final_s_max}")

    # 6. Exportar CSV
    filas_csv = []
    for (origen, destino), slots in sorted(espectro_final.items()):
        registro = {"Nodo_Origen": origen, "Nodo_Destino": destino}
        for i in range(TOTAL_SLOTS):
            registro[f"Slot_{i+1}"] = slots[i]
        filas_csv.append(registro)
    pd.DataFrame(filas_csv).to_csv(OUTPUT_OCCUPATION_CSV, index=False)
    print(f"\n  Matriz exportada: {OUTPUT_OCCUPATION_CSV}")

    # 7. Reporte de texto
    with open(OUTPUT_REPORT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("  REPORTE: ASIGNACIÓN DE DEMANDAS REFEFO CON MILP (PuLP-CBC)\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Estado base: {BASE_OCCUPATION_CSV}\n")
        f.write(f"Demandas:    {DEMANDAS_REFEFO_CSV}\n")
        f.write(f"Big-M:       {M_BIG}\n")
        f.write(f"TimeLimit:   {TIME_LIMIT}s | GapRel: {GAP_REL}\n\n")
        f.write("--- ESTADO BASE ---\n")
        f.write(f"  Enlaces:          {len(base_espectro)}\n")
        f.write(f"  Slots ocupados:   {base_slots_ocupados} / {base_total_slots}\n")
        f.write(f"  S_max:            {base_s_max}\n\n")
        f.write("--- MODELO MILP ---\n")
        f.write(f"  Variables totales:    {total_vars}\n")
        f.write(f"  Restricciones:        {total_constraints}\n")
        f.write(f"  Vars base (z):        {z_count}\n")
        f.write(f"  Vars solapamiento (x): {x_count}\n")
        f.write(f"  Estado solver:        {status_str}\n")
        f.write(f"  Tiempo:               {execution_time:.2f}s\n\n")
        f.write("--- RESULTADOS REFEFO ---\n")
        f.write(f"  Demandas REFEFO totales:        {total_demandas}\n")
        f.write(f"  Demandas asignadas con éxito:   {demandas_exitosas}\n")
        f.write(f"  Demandas bloqueadas:            {demandas_bloqueadas}\n")
        f.write(f"  Probabilidad de bloqueo:        {prob_bloqueo:.2f}%\n\n")
        f.write("--- ESTADO FINAL DE LA RED ---\n")
        f.write(f"  Enlaces:          {len(espectro_final)}\n")
        f.write(f"  Slots ocupados:   {final_slots_ocu} / {final_total_slots}\n")
        f.write(f"  Ocupación:        {final_ocu_pct:.2f}%\n")
        f.write(f"  S_max:            {final_s_max}\n\n")
        f.write(f"  Δ Slots ocupados: +{delta_slots}\n")
        f.write(f"  Δ S_max:          {base_s_max} → {final_s_max}\n\n")
        f.write("--- DETALLE POR DEMANDA ---\n")
        hdr = f"{'Iter':>5} | {'Source':<25} | {'Destination':<25} | {'Gbps':>5} | {'Resultado':<35} | {'K_Path':>6} | {'Slot':>5}\n"
        f.write(hdr)
        f.write("-" * 125 + "\n")
        for entry in log_detalle:
            f.write(
                f"{entry['Iteración']:5d} | {entry['Source']:<25} | "
                f"{entry['Destination']:<25} | {entry['Gbps']:5.0f} | "
                f"{entry['Resultado']:<35} | {str(entry['K_Path_Asignado']):>6} | "
                f"{str(entry.get('Slot_Inicio', '-')):>5}\n"
            )

    print(f"  Reporte exportado: {OUTPUT_REPORT_TXT}")
    print(f"\n{'=' * 70}")
    print("  PROCESO COMPLETADO")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
