"""
Asignación de demandas REFEFO sobre la red base con First-Fit.

Flujo:
  1. Carga la matriz espectral base desde 'ocupacion_base_firstfit.csv'.
  2. Lee las demandas REFEFO desde 'demandas_refefo.csv'.
  3. Para cada iteración (demanda), ordena los K-paths. Primero intenta
     los paths factibles (Direct_Feasible o Reg_Feasible). Si no hay
     factibles, intenta TODOS los K-paths igualmente.
  4. Si algún K-path tiene espectro disponible → ASIGNADA.
     Si ninguno tiene espectro → BLOQUEADA.
  5. Exporta la matriz espectral final y un reporte de estadísticas.
"""

import pandas as pd
import re
import os
import sys

# Estructura: script está en refefo/first_fit/
# REFEFO_DIR → refefo/       (un nivel arriba del script)
# PUNTO5_DIR → Pablo_punto5/ (dos niveles arriba del script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REFEFO_DIR = os.path.dirname(SCRIPT_DIR)
PUNTO5_DIR = os.path.dirname(REFEFO_DIR)

BASE_OCCUPATION_CSV = os.path.abspath(os.path.join(PUNTO5_DIR, "base", "first_fit", "ocupacion_base_firstfit.csv"))
DEMANDAS_REFEFO_CSV = os.path.join(REFEFO_DIR, "demandas_refefo.csv")
OUTPUT_OCCUPATION_CSV = os.path.join(SCRIPT_DIR, "ocupacion_refefo_firstfit.csv")
OUTPUT_REPORT_TXT = os.path.join(SCRIPT_DIR, "reporte_refefo_firstfit.txt")


# =============================================================================
# CLASE DE RED (reutiliza la lógica original de asignacion_first_fit.py)
# =============================================================================
class RedFlexiGridConsolidada:
    def __init__(self):
        """Inicializa la matriz espectral de la red."""
        self.espectro = {}

    def garantizar_enlace(self, par_enlace):
        """Crea el tramo orientado si no existe, con 304 slots libres."""
        if par_enlace not in self.espectro:
            self.espectro[par_enlace] = [""] * 304

    def cargar_desde_csv(self, csv_path):
        """
        Carga la ocupación espectral desde un CSV con formato:
        Nodo_Origen, Nodo_Destino, Slot_1 ... Slot_304
        """
        print(f"  Cargando estado base desde: {csv_path}")
        df = pd.read_csv(csv_path)

        for _, fila in df.iterrows():
            origen = fila["Nodo_Origen"]
            destino = fila["Nodo_Destino"]
            par = (origen, destino)
            slots = []
            for i in range(1, 305):
                val = fila[f"Slot_{i}"]
                # pandas lee celdas vacías como NaN
                if pd.isna(val):
                    slots.append("")
                else:
                    slots.append(str(val))
            self.espectro[par] = slots

        n_enlaces = len(self.espectro)
        slots_ocupados = sum(
            1 for slots in self.espectro.values()
            for s in slots if s != ""
        )
        print(f"  → {n_enlaces} enlaces cargados, {slots_ocupados} slots ocupados en total.")

    def asignar_first_fit(self, id_demanda, lista_enlaces, slots_necesarios):
        """
        Busca el PRIMER bloque contiguo libre alineado en todos los enlaces
        de la ruta. Si está libre, escribe la etiqueta de la demanda.
        Retorna True si la asignación fue exitosa, False si hay bloqueo.
        """
        # Asegurar que todos los tramos existan
        for enlace in lista_enlaces:
            self.garantizar_enlace(enlace)

        # Recorrer los 304 slots de izquierda a derecha
        for start_slot in range(304 - slots_necesarios + 1):
            libre_en_toda_la_ruta = True

            # Verificar si la ventana está libre en toda la ruta
            for enlace in lista_enlaces:
                bloque = self.espectro[enlace][start_slot : start_slot + slots_necesarios]
                if any(slot_celda != "" for slot_celda in bloque):
                    libre_en_toda_la_ruta = False
                    break

            # Si está libre, grabar la etiqueta
            if libre_en_toda_la_ruta:
                for enlace in lista_enlaces:
                    for k in range(start_slot, start_slot + slots_necesarios):
                        self.espectro[enlace][k] = id_demanda
                return True

        return False

    def exportar_csv_final(self, nombre_archivo):
        """
        Exporta la matriz consolidada con formato:
        Nodo_Origen, Nodo_Destino, Slot_1 ... Slot_304
        """
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

    def calcular_estadisticas(self):
        """Calcula estadísticas de ocupación de la red."""
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
    print("  ASIGNACIÓN DE DEMANDAS REFEFO CON FIRST-FIT")
    print("  Sobre estado base: ocupacion_base_firstfit.csv")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Cargar estado base de la red
    # ------------------------------------------------------------------
    red = RedFlexiGridConsolidada()
    red.cargar_desde_csv(BASE_OCCUPATION_CSV)

    stats_base = red.calcular_estadisticas()
    print(f"\n  Estado base de la red:")
    print(f"    Enlaces: {stats_base['total_enlaces']}")
    print(f"    Slots ocupados: {stats_base['slots_ocupados']} / {stats_base['total_slots']}")
    print(f"    Ocupación: {stats_base['ocupacion_pct']:.2f}%")
    print(f"    Slot máximo utilizado (S_max): {stats_base['slot_max_utilizado']}")

    # ------------------------------------------------------------------
    # 2. Cargar demandas REFEFO
    # ------------------------------------------------------------------
    print(f"\n  Cargando demandas REFEFO desde: {DEMANDAS_REFEFO_CSV}")
    df_refefo = pd.read_csv(DEMANDAS_REFEFO_CSV)
    iteraciones = sorted(df_refefo["Iteración"].unique())
    print(f"  → {len(iteraciones)} iteraciones (demandas) a procesar")
    print(f"  → {len(df_refefo)} filas totales (incluyendo K-paths)")

    # ------------------------------------------------------------------
    # 3. Procesar cada demanda (iteración)
    # ------------------------------------------------------------------
    demandas_exitosas = 0
    demandas_bloqueadas = 0

    log_detalle = []  # Para el reporte

    print(f"\n  Ejecutando asignación First-Fit incremental...")
    print("-" * 70)

    for iter_id in iteraciones:
        # Obtener todas las filas de esta iteración, ordenadas por K_Path
        df_iter = df_refefo[df_refefo["Iteración"] == iter_id].sort_values("K_Path")

        # Datos de la demanda (comunes a todos los K-paths)
        source = df_iter.iloc[0]["Source"]
        destination = df_iter.iloc[0]["Destination"]
        gbps = df_iter.iloc[0]["Gbps"]
        slots_necesarios = calcular_slots(gbps)

        # Filtrar los K-paths factibles (Direct_Feasible o Reg_Feasible)
        df_factibles = df_iter[
            (df_iter["Direct_Feasible"] == True) | (df_iter["Reg_Feasible"] == True)
        ]

        # Si hay paths factibles, intentar esos primero.
        # Si no hay ninguno factible, intentar TODOS los K-paths igualmente.
        if len(df_factibles) > 0:
            df_a_intentar = df_factibles
            tiene_factibles = True
        else:
            df_a_intentar = df_iter
            tiene_factibles = False

        # Intentar asignar con First-Fit en cada K-path (en orden)
        asignado = False
        for _, fila in df_a_intentar.iterrows():
            k_path = fila["K_Path"]
            path_sequence = fila["Path_Sequence"]

            # Extraer los pares de enlaces de la ruta
            enlaces = extraer_pares_nodo_a_nodo(path_sequence)

            # Generar etiqueta de demanda
            origen_norm = normalizar_ciudad(source)
            destino_norm = normalizar_ciudad(destination)
            id_demanda = f"{origen_norm}-{destino_norm}_{int(gbps)}G_ref{iter_id}"

            # Intentar asignación First-Fit
            exito = red.asignar_first_fit(id_demanda, enlaces, slots_necesarios)

            if exito:
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
                tag_print = " (sin GSNR factible)" if not tiene_factibles else ""
                print(f"  [OK]  Iter {iter_id:3d}: {source} → {destination} "
                      f"({int(gbps)}G, K={k_path}, {slots_necesarios} slots){tag_print}")
                break

        if not asignado:
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

    # ------------------------------------------------------------------
    # 4. Estadísticas finales
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  REPORTE FINAL")
    print("=" * 70)

    total_demandas = len(iteraciones)

    stats_final = red.calcular_estadisticas()

    print(f"\n  Demandas REFEFO totales:        {total_demandas}")
    print(f"  Demandas asignadas con éxito:   {demandas_exitosas}")
    print(f"  Demandas bloqueadas:            {demandas_bloqueadas}")

    if total_demandas > 0:
        prob_bloqueo = (demandas_bloqueadas / total_demandas) * 100
        print(f"\n  Probabilidad de bloqueo:        {prob_bloqueo:.2f}%")
    else:
        prob_bloqueo = 0.0
        print(f"\n  Probabilidad de bloqueo:        N/A")

    print(f"\n  Estado final de la red:")
    print(f"    Enlaces: {stats_final['total_enlaces']}")
    print(f"    Slots ocupados: {stats_final['slots_ocupados']} / {stats_final['total_slots']}")
    print(f"    Ocupación: {stats_final['ocupacion_pct']:.2f}%")
    print(f"    Slot máximo utilizado (S_max): {stats_final['slot_max_utilizado']}")

    delta_slots = stats_final['slots_ocupados'] - stats_base['slots_ocupados']
    print(f"\n  Δ Slots ocupados (refefo):      +{delta_slots}")
    print(f"  Δ S_max:                        {stats_base['slot_max_utilizado']} → {stats_final['slot_max_utilizado']}")

    # ------------------------------------------------------------------
    # 5. Exportar resultados
    # ------------------------------------------------------------------
    red.exportar_csv_final(OUTPUT_OCCUPATION_CSV)

    # Reporte de texto
    with open(OUTPUT_REPORT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("  REPORTE: ASIGNACIÓN DE DEMANDAS REFEFO CON FIRST-FIT\n")
        f.write("=" * 70 + "\n\n")

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

        f.write("--- ESTADO FINAL DE LA RED ---\n")
        f.write(f"  Enlaces:          {stats_final['total_enlaces']}\n")
        f.write(f"  Slots ocupados:   {stats_final['slots_ocupados']} / {stats_final['total_slots']}\n")
        f.write(f"  Ocupación:        {stats_final['ocupacion_pct']:.2f}%\n")
        f.write(f"  S_max:            {stats_final['slot_max_utilizado']}\n\n")

        f.write(f"  Δ Slots ocupados: +{delta_slots}\n")
        f.write(f"  Δ S_max:          {stats_base['slot_max_utilizado']} → {stats_final['slot_max_utilizado']}\n\n")

        f.write("--- DETALLE POR DEMANDA ---\n")
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
