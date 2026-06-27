"""
Asignación de demandas REFEFO sobre la red base con First-Fit, incluyendo métricas de calidad.

Flujo:
  1. Carga la matriz espectral base y reconstruye las solicitudes del escenario base.
  2. Lee las demandas REFEFO desde 'demandas_refefo.csv'.
  3. Para cada iteración (demanda), mide el tiempo de ruteo y asignación.
  4. Ordena los K-paths por GSNR y busca asignar. Si se bloquea, registra el bloqueo en el camino primario.
  5. Calcula y reporta las métricas de calidad (tiempos desglosados, P_bloqueo por enlace, fragmentación, contigüidad y carga).
  6. Exporta los archivos de salida correspondientes.
"""

import pandas as pd
import re
import os
import sys
import time

# Estructura: script está en refefo/first_fit/py/
# SCRIPT_DIR → refefo/first_fit/py
# FF_DIR → refefo/first_fit (un nivel arriba)
# REFEFO_DIR → refefo/       (dos niveles arriba)
# RSA_DIR → RSA/             (tres niveles arriba)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FF_DIR = os.path.dirname(SCRIPT_DIR)
REFEFO_DIR = os.path.dirname(FF_DIR)
RSA_DIR = os.path.dirname(REFEFO_DIR)

BASE_OCCUPATION_V3_CSV = os.path.abspath(os.path.join(RSA_DIR, "base", "first_fit", "ocupacion_base_firstfit_V3_metricas.csv"))
BASE_OCCUPATION_V2_CSV = os.path.abspath(os.path.join(RSA_DIR, "base", "first_fit", "ocupacion_base_firstfit_V2.csv"))
BASE_OCCUPATION_CSV = BASE_OCCUPATION_V3_CSV if os.path.exists(BASE_OCCUPATION_V3_CSV) else BASE_OCCUPATION_V2_CSV

BASE_MAPPING_V3_CSV = os.path.abspath(os.path.join(RSA_DIR, "base", "first_fit", "mapping_lightpaths_firstfit_V3_metricas.csv"))
BASE_MAPPING_V2_CSV = os.path.abspath(os.path.join(RSA_DIR, "base", "first_fit", "mapping_lightpaths_firstfit.csv"))
BASE_MAPPING_CSV = BASE_MAPPING_V3_CSV if os.path.exists(BASE_MAPPING_V3_CSV) else BASE_MAPPING_V2_CSV

BASE_DEMANDAS_V3_CSV = os.path.abspath(os.path.join(RSA_DIR, "base", "first_fit", "lista_demandas_firstfit_V3_metricas.csv"))
BASE_DEMANDAS_V2_CSV = os.path.abspath(os.path.join(RSA_DIR, "base", "first_fit", "lista_demandas_firstfit.csv"))
BASE_DEMANDAS_CSV = BASE_DEMANDAS_V3_CSV if os.path.exists(BASE_DEMANDAS_V3_CSV) else BASE_DEMANDAS_V2_CSV

DEMANDAS_REFEFO_CSV = os.path.join(REFEFO_DIR, "demandas_refefo.csv")

OUTPUT_OCCUPATION_CSV = os.path.join(FF_DIR, "ocupacion_refefo_firstfit_metricas.csv")
OUTPUT_REPORT_TXT = os.path.join(FF_DIR, "reporte_refefo_firstfit_metricas.txt")
OUTPUT_MAPPING_CSV = os.path.join(FF_DIR, "mapping_lightpaths_refefo_metricas.csv")
OUTPUT_DEMANDAS_CSV = os.path.join(FF_DIR, "lista_demandas_refefo_metricas.csv")


# =============================================================================
# CLASE DE RED (reutiliza la lógica original y agrega soporte para métricas)
# =============================================================================
class RedFlexiGridConsolidada:
    def __init__(self):
        """Inicializa la matriz espectral de la red."""
        self.espectro = {}
        self.link_requests = {}
        self.link_blocks = {}

    def garantizar_enlace(self, par_enlace):
        """Crea el tramo orientado si no existe, con 304 slots libres."""
        if par_enlace not in self.espectro:
            self.espectro[par_enlace] = [""] * 304

    def registrar_intento(self, lista_enlaces, fue_bloqueado):
        """Registra solicitudes y bloqueos por enlace."""
        for enlace in lista_enlaces:
            self.garantizar_enlace(enlace)
            self.link_requests[enlace] = self.link_requests.get(enlace, 0) + 1
            if fue_bloqueado:
                self.link_blocks[enlace] = self.link_blocks.get(enlace, 0) + 1

    def cargar_desde_csv(self, csv_path):
        """
        Carga la ocupación espectral desde un CSV y reconstruye las solicitudes base.
        """
        print(f"  Cargando estado base desde: {csv_path}")
        df = pd.read_csv(csv_path)

        for _, fila in df.iterrows():
            origen = fila["Nodo_Origen"]
            destino = fila["Nodo_Destino"]
            par = (origen, destino)
            slots = []
            
            demandas_en_enlace = set()
            for i in range(1, 305):
                val = fila[f"Slot_{i}"]
                if pd.isna(val):
                    slots.append("")
                else:
                    val_str = str(val).strip()
                    slots.append(val_str)
                    if val_str != "" and val_str != "nan":
                        demandas_en_enlace.add(val_str)
                        
            self.espectro[par] = slots
            # Inicializar con las solicitudes exitosas de la base (0 bloqueos)
            self.link_requests[par] = len(demandas_en_enlace)
            self.link_blocks[par] = 0

        n_enlaces = len(self.espectro)
        slots_ocupados = sum(
            1 for slots in self.espectro.values()
            for s in slots if s != ""
        )
        print(f"  → {n_enlaces} enlaces cargados, {slots_ocupados} slots ocupados en total.")

    def asignar_first_fit(self, id_demanda, lista_enlaces, slots_necesarios):
        """
        Busca el PRIMER bloque contiguo libre alineado en todos los enlaces de la ruta.
        """
        for enlace in lista_enlaces:
            self.garantizar_enlace(enlace)

        for start_slot in range(304 - slots_necesarios + 1):
            libre_en_toda_la_ruta = True

            for enlace in lista_enlaces:
                bloque = self.espectro[enlace][start_slot : start_slot + slots_necesarios]
                if any(slot_celda != "" for slot_celda in bloque):
                    libre_en_toda_la_ruta = False
                    break

            if libre_en_toda_la_ruta:
                for enlace in lista_enlaces:
                    for k in range(start_slot, start_slot + slots_necesarios):
                        self.espectro[enlace][k] = id_demanda
                return True

        return False

    def exportar_csv_final(self, nombre_archivo):
        """Exporta la matriz consolidada."""
        filas_salida = []
        for (origen, destino), slots in sorted(self.espectro.items()):
            registro = {
                "Nodo_Origen": origen,
                "Nodo_Destino": destino
            }
            for i in range(304):
                registro[f"Slot_{i+1}"] = slots[i]
            filas_salida.append(registro)

        df_salida = pd.DataFrame(filas_salida)
        df_salida.to_csv(nombre_archivo, index=False)
        print(f"  Matriz exportada: {nombre_archivo}")

    def calcular_metricas_calidad(self):
        """Calcula estadísticas enlace por enlace de la red."""
        metricas_enlaces = {}
        
        for enlace, slots in self.espectro.items():
            total_slots = len(slots)
            slots_ocupados = sum(1 for s in slots if s != "")
            slots_libres = total_slots - slots_ocupados
            
            # Encontrar bloques contiguos de slots libres
            bloques_libres = []
            bloque_actual = 0
            for s in slots:
                if s == "":
                    bloque_actual += 1
                else:
                    if bloque_actual > 0:
                        bloques_libres.append(bloque_actual)
                        bloque_actual = 0
            if bloque_actual > 0:
                bloques_libres.append(bloque_actual)
                
            # Fragmentación y Contigüidad
            if slots_libres == 0:
                fragmentacion = 1.0
                contiguidad = 0.0
                max_bloque_libre = 0
            else:
                max_bloque_libre = max(bloques_libres) if bloques_libres else 0
                fragmentacion = 1.0 - (max_bloque_libre / slots_libres)
                sum_sq_bloques = sum(b**2 for b in bloques_libres)
                contiguidad = sum_sq_bloques / (slots_libres**2)
                
            # Variaciones de ocupado a libre
            transiciones = sum(1 for i in range(1, len(slots)) if slots[i-1] != "" and slots[i] == "")

            # Probabilidad de bloqueo por enlace
            requests = self.link_requests.get(enlace, 0)
            blocks = self.link_blocks.get(enlace, 0)
            prob_bloqueo = (blocks / requests * 100) if requests > 0 else 0.0
            
            metricas_enlaces[enlace] = {
                "slots_ocupados": slots_ocupados,
                "slots_libres": slots_libres,
                "fragmentacion": fragmentacion,
                "contiguidad": contiguidad,
                "max_bloque_libre": max_bloque_libre,
                "transiciones_occ_lib": transiciones,
                "solicitudes": requests,
                "bloqueos": blocks,
                "prob_bloqueo_pct": prob_bloqueo
            }
            
        return metricas_enlaces

    def calcular_estadisticas_basicas(self):
        """Calcula estadísticas de ocupación globales básicas."""
        total_slots = 0
        slots_ocupados = 0
        slot_max_global = 0

        for (origen, destino), slots in self.espectro.items():
            total_slots += 304
            for i, s in enumerate(slots):
                if s != "":
                    slots_ocupados += 1
                    if (i + 1) > slot_max_global:
                        slot_max_global = i + 1

        ocupacion_pct = (slots_ocupados / total_slots * 100) if total_slots > 0 else 0
        return {
            "total_enlaces": len(self.espectro),
            "total_slots": total_slots,
            "slots_ocupados": slots_ocupados,
            "slots_libres": total_slots - slots_ocupados,
            "ocupacion_pct": ocupacion_pct,
            "slot_max_utilizado": slot_max_global,
        }


# =============================================================================
# DICCIONARIO DE NORMALIZACIÓN (idéntico al original)
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
    """Normaliza un nombre de ciudad al formato 'roadm NombreNormalizado'."""
    nombre_limpio = nombre_ciudad.strip()
    nombre_limpio = re.sub(r'^roadm\s+', '', nombre_limpio)
    nombre_corregido = DICCIONARIO_NOMBRES.get(nombre_limpio, nombre_limpio)
    return f"roadm {nombre_corregido}"


def extraer_pares_nodo_a_nodo(ruta_str):
    """
    Convierte una ruta de texto tipo 'Ciudad1 - Ciudad2 - Ciudad3'
    en pares secuenciales de roadms: [(roadm Ciudad1, roadm Ciudad2), ...]
    """
    ciudades = [c.strip() for c in re.split(r'\s*-\s*|\s*→\s*', ruta_str) if c.strip()]
    nodos_roadm = [normalizar_ciudad(ciudad) for ciudad in ciudades]

    pares = []
    for i in range(len(nodos_roadm) - 1):
        pares.append((nodos_roadm[i], nodos_roadm[i + 1]))
    return pares


def calcular_slots(gbps):
    """Determina la cantidad de slots necesarios según la velocidad."""
    if gbps in [100, 200, 100.0, 200.0]:
        return 4
    else:  # 300, 400
        return 6


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================
def main():
    print("=" * 70)
    print("  ASIGNACIÓN DE DEMANDAS REFEFO CON FIRST-FIT (V3 - MÉTRICAS)")
    print(f"  Sobre estado base: {BASE_OCCUPATION_CSV}")
    print("=" * 70)

    # 1. Cargar estado base de la red y solicitudes base
    red = RedFlexiGridConsolidada()
    red.cargar_desde_csv(BASE_OCCUPATION_CSV)

    stats_base = red.calcular_estadisticas_basicas()
    print(f"\n  Estado base de la red:")
    print(f"    Enlaces: {stats_base['total_enlaces']}")
    print(f"    Slots ocupados: {stats_base['slots_ocupados']} / {stats_base['total_slots']}")
    print(f"    Ocupación: {stats_base['ocupacion_pct']:.2f}%")
    print(f"    Slot máximo utilizado (S_max): {stats_base['slot_max_utilizado']}")

    # 2. Cargar demandas REFEFO
    print(f"\n  Cargando demandas REFEFO desde: {DEMANDAS_REFEFO_CSV}")
    df_refefo = pd.read_csv(DEMANDAS_REFEFO_CSV)
    iteraciones = sorted(df_refefo["Iteración"].unique())
    print(f"  → {len(iteraciones)} iteraciones (demandas) a procesar")
    print(f"  → {len(df_refefo)} filas totales (incluyendo K-paths)")

    # 3. Procesar cada demanda (iteración)
    demandas_exitosas = 0
    demandas_bloqueadas = 0
    refefo_mapping = []
    refefo_demands = []
    log_detalle = []  # Para el reporte
    
    # Lista para registrar los tiempos de ejecución por demanda individual
    tiempos_demandas = []

    print(f"\n  Ejecutando asignación First-Fit incremental...")
    print("-" * 70)

    for iter_id in iteraciones:
        # --- INICIO MEDICIÓN TIEMPO DEMANDA REFEFO ---
        t0 = time.perf_counter()
        
        # Obtener todas las filas de esta iteración, ordenadas por mejor GSNR
        df_iter = df_refefo[df_refefo["Iteración"] == iter_id].sort_values("GSNR_Direct", ascending=False)

        # Datos de la demanda (comunes a todos los K-paths)
        source = df_iter.iloc[0]["Source"]
        destination = df_iter.iloc[0]["Destination"]
        gbps = df_iter.iloc[0]["Gbps"]
        slots_necesarios = calcular_slots(gbps)

        # Filtrar los K-paths factibles (Direct_Feasible o Reg_Feasible)
        df_factibles = df_iter[
            (df_iter["Direct_Feasible"] == True) | (df_iter["Reg_Feasible"] == True)
        ]

        if len(df_factibles) > 0:
            df_a_intentar = df_factibles
            tiene_factibles = True
        else:
            df_a_intentar = df_iter
            tiene_factibles = False

        # Intentar asignar con First-Fit en cada K-path (en orden)
        asignado = False
        primary_enlaces = None
        
        for path_idx, (_, fila) in enumerate(df_a_intentar.iterrows()):
            k_path = fila["K_Path"]
            path_sequence = fila["Path_Sequence"]

            # Extraer los pares de enlaces de la ruta
            enlaces = extraer_pares_nodo_a_nodo(path_sequence)
            
            # Guardamos la ruta preferida (la primera del ordenamiento por GSNR)
            if path_idx == 0:
                primary_enlaces = enlaces

            # Generar etiqueta de demanda
            origen_norm = normalizar_ciudad(source)
            destino_norm = normalizar_ciudad(destination)
            id_demanda = f"{origen_norm}-{destino_norm}_{int(gbps)}G_ref{iter_id}"

            # Intentar asignación First-Fit
            exito = red.asignar_first_fit(id_demanda, enlaces, slots_necesarios)

            if exito:
                # Éxito: registramos solicitud en esta ruta asignada
                red.registrar_intento(enlaces, fue_bloqueado=False)
                
                # Fin de medición de tiempo para asignación exitosa
                t_elapsed = time.perf_counter() - t0
                tiempos_demandas.append(t_elapsed)
                
                demandas_exitosas += 1
                asignado = True
                tag_fact = "" if tiene_factibles else " [no-fact]"
                log_detalle.append({
                    "Iteración": iter_id,
                    "Source": source,
                    "Destination": destination,
                    "Gbps": gbps,
                    "Resultado": f"ASIGNADA{tag_fact}",
                    "K_Path_Asignado": k_path,
                    "Slots_Asignados": slots_necesarios,
                })
                refefo_mapping.append({
                    "Nombre_Lightpath": id_demanda,
                    "ID_Demanda": f"R{iter_id}",
                    "Velocidad": f"{int(gbps)}G",
                    "Instancia": 1
                })
                refefo_demands.append({
                    "ID_Demanda": f"R{iter_id}",
                    "Origen": source,
                    "Destino": destination,
                    "Cantidad de Enlaces": 1,
                    "Velocidad [Gbps]": int(gbps),
                    "Ruta": path_sequence
                })
                tag_print = " (sin GSNR factible)" if not tiene_factibles else ""
                print(f"  [OK]  Iter {iter_id:3d}: {source} → {destination} "
                      f"({int(gbps)}G, K={k_path}, {slots_necesarios} slots){tag_print}")
                break

        if not asignado:
            # Bloqueo: registramos solicitud y bloqueo en la ruta preferida (de mayor GSNR)
            if primary_enlaces:
                red.registrar_intento(primary_enlaces, fue_bloqueado=True)
                
            # Fin de medición de tiempo para bloqueo
            t_elapsed = time.perf_counter() - t0
            tiempos_demandas.append(t_elapsed)
            
            demandas_bloqueadas += 1
            tag_fact = "sin paths factibles" if not tiene_factibles else "sin espectro"
            log_detalle.append({
                "Iteración": iter_id,
                "Source": source,
                "Destination": destination,
                "Gbps": gbps,
                "Resultado": f"BLOQUEADA ({tag_fact})",
                "K_Path_Asignado": "-",
                "Slots_Asignados": 0,
            })
            print(f"  [BLOQ] Iter {iter_id:3d}: {source} → {destination} "
                  f"({int(gbps)}G) - {tag_fact.upper()} en {len(df_a_intentar)} paths")

    # 4. Calcular métricas finales de calidad
    stats_enlaces = red.calcular_metricas_calidad()
    
    # ----------------------------------------------------
    # Procesar métricas generales de calidad acumuladas (Base + REFEFO)
    # ----------------------------------------------------
    # 1. Tiempos desglosados (solo REFEFO, ya que mide este algoritmo sobre la red)
    min_time = min(tiempos_demandas) if tiempos_demandas else 0
    max_time = max(tiempos_demandas) if tiempos_demandas else 0
    avg_time = (sum(tiempos_demandas) / len(tiempos_demandas)) if tiempos_demandas else 0
    
    # 2. Fragmentación y contigüidad promedios
    frag_list = [info["fragmentacion"] for info in stats_enlaces.values()]
    contig_list = [info["contiguidad"] for info in stats_enlaces.values()]
    max_free_block_list = [info["max_bloque_libre"] for info in stats_enlaces.values()]
    
    avg_frag = sum(frag_list) / len(frag_list) if frag_list else 0
    avg_contig = sum(contig_list) / len(contig_list) if contig_list else 0
    avg_max_free_block = sum(max_free_block_list) / len(max_free_block_list) if max_free_block_list else 0
    
    # 3. Variación de la carga
    occ_list = [info["slots_ocupados"] for info in stats_enlaces.values()]
    min_occ = min(occ_list) if occ_list else 0
    max_occ = max(occ_list) if occ_list else 0
    var_occ = max_occ - min_occ
    avg_occ = sum(occ_list) / len(occ_list) if occ_list else 0
    
    # 4. Probabilidad de bloqueo promedio por enlace (acumulado)
    block_prob_list = [info["prob_bloqueo_pct"] for info in stats_enlaces.values()]
    avg_link_block_prob = sum(block_prob_list) / len(block_prob_list) if block_prob_list else 0

    # 5. Transiciones ocupado-a-libre
    trans_list = [info["transiciones_occ_lib"] for info in stats_enlaces.values()]
    min_trans = min(trans_list) if trans_list else 0
    max_trans = max(trans_list) if trans_list else 0
    avg_trans = sum(trans_list) / len(trans_list) if trans_list else 0

    print("\n" + "=" * 70)
    print("  REPORTE FINAL CON MÉTRICAS DE CALIDAD ACUMULADAS")
    print("=" * 70)

    total_demandas = len(iteraciones)
    stats_final = red.calcular_estadisticas_basicas()

    print(f"\n  Demandas REFEFO procesadas:     {total_demandas}")
    print(f"  Demandas REFEFO exitosas:       {demandas_exitosas}")
    print(f"  Demandas REFEFO bloqueadas:     {demandas_bloqueadas}")

    if total_demandas > 0:
        prob_bloqueo = (demandas_bloqueadas / total_demandas) * 100
        print(f"  Probabilidad de bloqueo REFEFO: {prob_bloqueo:.2f}%")
    else:
        prob_bloqueo = 0.0
        print(f"  Probabilidad de bloqueo REFEFO: N/A")

    print("\n--- METRICAS DE TIEMPO POR DEMANDA REFEFO INDIVIDUAL ---")
    print(f"  Tiempo mínimo:  {min_time*1000:.4f} ms")
    print(f"  Tiempo máximo:  {max_time*1000:.4f} ms")
    print(f"  Tiempo promedio: {avg_time*1000:.4f} ms")
    
    print("\n--- METRICAS DE GRIDS Y ESPECTRO DE LA RED (ESTADO FINAL) ---")
    print(f"  Ocupación promedio de slots por enlace: {avg_occ:.2f} slots ({avg_occ/304*100:.2f}%)")
    print(f"  Enlace menos cargado: {min_occ} slots | Enlace más cargado: {max_occ} slots")
    print(f"  Variación de la carga (Max - Min): {var_occ} slots")
    print(f"  Fragmentación espectral promedio de la red: {avg_frag:.4f}")
    print(f"  Contigüidad espectral promedio de la red:   {avg_contig:.4f}")
    print(f"  Tamaño promedio del bloque libre máximo:    {avg_max_free_block:.2f} slots")
    print(f"  Transiciones ocupado-a-libre promedio:      {avg_trans:.4f} (mín: {min_trans}, máx: {max_trans})")
    print(f"  Probabilidad de bloqueo promedio por enlace: {avg_link_block_prob:.4f}%")

    delta_slots = stats_final['slots_ocupados'] - stats_base['slots_ocupados']
    print(f"\n  Δ Slots ocupados (refefo):      +{delta_slots}")
    print(f"  Δ S_max:                        {stats_base['slot_max_utilizado']} → {stats_final['slot_max_utilizado']}")

    # 5. Exportar resultados
    red.exportar_csv_final(OUTPUT_OCCUPATION_CSV)

    # Guardar mapeo consolidado
    df_base_map = pd.read_csv(BASE_MAPPING_CSV) if os.path.exists(BASE_MAPPING_CSV) else pd.DataFrame()
    df_ref_map = pd.DataFrame(refefo_mapping)
    df_consolidated_map = pd.concat([df_base_map, df_ref_map], ignore_index=True)
    df_consolidated_map.to_csv(OUTPUT_MAPPING_CSV, index=False)
    print(f" Mapeo consolidado de lightpaths exportado: {OUTPUT_MAPPING_CSV}")

    # Guardar lista de demandas consolidada
    df_base_dem = pd.read_csv(BASE_DEMANDAS_CSV) if os.path.exists(BASE_DEMANDAS_CSV) else pd.DataFrame()
    df_ref_dem = pd.DataFrame(refefo_demands)
    df_consolidated_dem = pd.concat([df_base_dem, df_ref_dem], ignore_index=True)
    df_consolidated_dem.to_csv(OUTPUT_DEMANDAS_CSV, index=False)
    print(f" Lista de demandas consolidada exportada: {OUTPUT_DEMANDAS_CSV}")

    # Reporte de texto detallado por enlace
    with open(OUTPUT_REPORT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("  REPORTE COMPLETO: ASIGNACIÓN DE DEMANDAS REFEFO CON FIRST-FIT Y MÉTODOS DE CALIDAD\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Estado base: {BASE_OCCUPATION_CSV}\n")
        f.write(f"Demandas:    {DEMANDAS_REFEFO_CSV}\n\n")

        f.write("--- ESTADO BASE ---\n")
        f.write(f"  Enlaces:          {stats_base['total_enlaces']}\n")
        f.write(f"  Slots ocupados:   {stats_base['slots_ocupados']} / {stats_base['total_slots']}\n")
        f.write(f"  Ocupación:        {stats_base['ocupacion_pct']:.2f}%\n")
        f.write(f"  S_max:            {stats_base['slot_max_utilizado']}\n\n")

        f.write("--- RESULTADOS REFEFO ---\n")
        f.write(f"  Demandas REFEFO totales:        {total_demandas}\n")
        f.write(f"  Demandas asignadas con éxito:   {demandas_exitosas}\n")
        f.write(f"  Demandas bloqueadas:            {demandas_bloqueadas}\n")
        f.write(f"  Probabilidad de bloqueo:        {prob_bloqueo:.2f}%\n\n")

        f.write("--- MÉTRIAS DE TIEMPO POR DEMANDA REFEFO INDIVIDUAL ---\n")
        f.write(f"  Tiempo mínimo:                  {min_time*1000:.4f} ms\n")
        f_rep_max = f"  Tiempo máximo:                  {max_time*1000:.4f} ms\n"
        f.write(f_rep_max)
        f.write(f"  Tiempo promedio:                {avg_time*1000:.4f} ms\n\n")

        f.write("--- ESTADO FINAL ACUMULADO DE LA RED ---\n")
        f.write(f"  Enlaces:          {stats_final['total_enlaces']}\n")
        f.write(f"  Slots ocupados:   {stats_final['slots_ocupados']} / {stats_final['total_slots']}\n")
        f.write(f"  Ocupación:        {stats_final['ocupacion_pct']:.2f}%\n")
        f.write(f"  S_max:            {stats_final['slot_max_utilizado']}\n\n")

        f.write(f"  Δ Slots ocupados: +{delta_slots}\n")
        f.write(f"  Δ S_max:          {stats_base['slot_max_utilizado']} → {stats_final['slot_max_utilizado']}\n")
        f.write(f"  Fragmentación Promedio:         {avg_frag:.6f}\n")
        f.write(f"  Contigüidad Promedio:           {avg_contig:.6f}\n")
        f.write(f"  Variación de Carga (Max-Min):   {var_occ} slots\n")
        f.write(f"  Transiciones Ocupado-Libre (min/max/prom): {min_trans} / {max_trans} / {avg_trans:.4f}\n")
        f.write(f"  Prob. Bloqueo Promedio Enlace:   {avg_link_block_prob:.4f}%\n\n")

        f.write("--- MÉTRIAS DETALLADAS ENLACE POR ENLACE ---\n")
        f.write(f"{'Enlace (Origen -> Destino)':<60} | {'Ocupados':<8} | {'Libres':<8} | {'Frag (F)':<8} | {'Contig (C)':<10} | {'Trans O->L':<10} | {'Solics':<7} | {'Bloqs':<6} | {'P_block%':<8}\n")
        f.write("-" * 148 + "\n")
        for enlace, info in sorted(stats_enlaces.items()):
            enlace_str = f"{enlace[0].replace('roadm ', '')} -> {enlace[1].replace('roadm ', '')}"
            f.write(f"{enlace_str:<60} | {info['slots_ocupados']:8d} | {info['slots_libres']:8d} | {info['fragmentacion']:8.4f} | {info['contiguidad']:10.4f} | {info['transiciones_occ_lib']:10d} | {info['solicitudes']:7d} | {info['bloqueos']:6d} | {info['prob_bloqueo_pct']:7.2f}%\n")

        f.write("\n--- DETALLE POR DEMANDA REFEFO ---\n")
        f.write(f"{'Iter':>5} | {'Source':<25} | {'Destination':<25} | {'Gbps':>5} | {'Resultado':<35} | {'K_Path':>6}\n")
        f.write("-" * 115 + "\n")
        for entry in log_detalle:
            f.write(
                f"{entry['Iteración']:5d} | {entry['Source']:<25} | "
                f"{entry['Destination']:<25} | {entry['Gbps']:5.0f} | "
                f"{entry['Resultado']:<35} | {str(entry['K_Path_Asignado']):>6}\n"
            )

    print(f"\n  Reporte exportado: {OUTPUT_REPORT_TXT}")
    print(f"\n{'=' * 70}")
    print("  PROCESO COMPLETADO")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
