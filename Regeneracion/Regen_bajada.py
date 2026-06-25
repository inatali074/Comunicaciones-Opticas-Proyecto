import json
import networkx as nx
import io
import re
import os
import sys
import copy
import tempfile
import pandas as pd
from contextlib import redirect_stdout

# --- Configuración de entorno ---
# Asegurar acceso a las librerías del venv
venv_site = os.path.join(sys.prefix, 'lib', 'python3.12', 'site-packages')
if venv_site not in sys.path:
    sys.path.append(venv_site)

from gnpy.tools.cli_examples import transmission_main_example

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NETWORK_JSON = os.path.join(SCRIPT_DIR, "..", "Consigna", "network_mashe.json")
EQUIPMENT_JSON = os.path.join(SCRIPT_DIR, "..", "Consigna", "equipament_real_marcos_corregido.json")
BASE_RESULTADOS = os.path.join(SCRIPT_DIR, "..", "resultados_gsnr_demandas_base.csv")
REGEN_RESULTADOS = os.path.join(SCRIPT_DIR, "resultados_gsnr_demandas_base_regenerado.csv")
OUTPUT_CSV = os.path.join(SCRIPT_DIR, "resultados_gsnr_demandas_base_regenerado_bajda_velocidad.csv")

def clean(name):
    """Limpia nombres para visualización y CSV."""
    return str(name).replace("roadm ", "").replace("trx ", "").strip()

def extract_gsnr(output_text):
    """Extrae el valor GSNR del output de GNPy."""
    matches = re.findall(r"GSNR \(0\.1nm, dB\):\s+([0-9.]+)", output_text)
    return float(matches[-1]) if matches else None

def sanitize_network(net):
    """Asegura consistencia en los ROADMs del JSON recortado."""
    valid_uids = {e["uid"] for e in net["elements"]}
    for e in net["elements"]:
        if e["type"] == "Roadm":
            params = e.get("params", {})
            for key in ["per_degree_pch_out_db", "per_degree_power_targets"]:
                if key in params:
                    params[key] = {k: v for k, v in params[key].items() if k in valid_uids}

_gnpy_cache = {}

def run_gnpy_on_path(path_elements, start_trx, end_trx, all_elements, all_connections):
    """Ejecuta simulación física directa en cada llamada."""
    if start_trx not in all_elements or end_trx not in all_elements:
        return None
        
    cache_key = (start_trx, end_trx)
    if cache_key in _gnpy_cache:
        return _gnpy_cache[cache_key]
        
    used_uids = set(path_elements + [start_trx, end_trx])

    network_trimmed = {
        "elements": [copy.deepcopy(all_elements[u]) for u in used_uids if u in all_elements],
        "connections": [c for c in all_connections if c["from_node"] in used_uids and c["to_node"] in used_uids]
    }

    sanitize_network(network_trimmed)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8") as tmp_file:
        json.dump(network_trimmed, tmp_file)
        tmp_path = tmp_file.name

    buffer = io.StringIO()
    args = ["--equipment", EQUIPMENT_JSON, tmp_path, start_trx, end_trx]

    try:
        with redirect_stdout(buffer):
            transmission_main_example(args)
    except SystemExit:
        pass
    except Exception as e:
        print(f"  [!] Error running GNPy for {start_trx} -> {end_trx}: {type(e).__name__}: {e}")
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        return None

    gsnr_val = extract_gsnr(buffer.getvalue())

    if os.path.exists(tmp_path):
        os.unlink(tmp_path)

    _gnpy_cache[cache_key] = gsnr_val
    return gsnr_val

def optimize_regeneration(full_path, target_osnr, all_elements, all_connections):
    """Calcula la ubicación de regeneradores si la señal es insuficiente."""
    roadms_trx = [
        n for n in full_path
        if all_elements[n]["type"] == "Roadm" and f"trx {clean(n)}" in all_elements
    ]

    if len(roadms_trx) < 2:
        return 0, [], [], False

    current_idx = 0
    reg_nodes = [clean(roadms_trx[0])]
    reg_gsnrs = []
    path_possible = True

    while current_idx < len(roadms_trx) - 1:
        best_idx = None
        best_gsnr = None
        for next_idx in range(len(roadms_trx) - 1, current_idx, -1):
            gsnr = run_gnpy_on_path(
                full_path,
                f"trx {clean(roadms_trx[current_idx])}",
                f"trx {clean(roadms_trx[next_idx])}",
                all_elements, all_connections
            )
            if gsnr is not None and gsnr >= target_osnr:
                best_idx = next_idx
                best_gsnr = gsnr
                break

        if best_idx is None:
            path_possible = False
            best_idx = current_idx + 1
            best_gsnr = run_gnpy_on_path(
                full_path,
                f"trx {clean(roadms_trx[current_idx])}",
                f"trx {clean(roadms_trx[best_idx])}",
                all_elements, all_connections
            )

        reg_nodes.append(clean(roadms_trx[best_idx]))
        reg_gsnrs.append(best_gsnr)
        current_idx = best_idx

    return len(reg_nodes) - 2, reg_nodes, reg_gsnrs, path_possible

def normalize_string(s):
    """Normaliza texto removiendo acentos, mayúsculas y aplicando sinónimos comunes."""
    if not isinstance(s, str):
        return ""
    s = s.strip().lower()
    
    # Mapeo de sinónimos/abreviaturas
    synonyms = {
        "v. mercedes": "villa mercedes",
        "gral. alvear": "general alvear",
        "saenz peña": "presidencia roque saenz peña",
        "sanz peña": "presidencia roque saenz peña",
        "j. de san martin": "jose de san martin",
        "esperanza (stacruz)": "esperanza",
        "tucuman": "san miguel de tucuman",
        "san miguel de tucumán": "san miguel de tucuman",
    }
    
    for k, v in synonyms.items():
        if k in s:
            s = s.replace(k, v)
            
    # Quitar acentos
    s = s.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ü", "u")
    s = s.replace("ñ", "n")
    
    # Limpiar espacios
    s = " ".join(s.split())
    return s

def find_node_for_city(city_name, node_type, all_elements, G, neighbor_node=None):
    """
    Encuentra el UID de un elemento del tipo dado (Transceiver o Roadm)
    que coincida con el nombre de la ciudad.
    Si hay múltiples candidatos, selecciona el más cercano al neighbor_node usando el grafo G.
    """
    search_term = normalize_string(city_name)
    
    candidates = []
    for uid, el in all_elements.items():
        if el["type"] == node_type:
            uid_norm = normalize_string(uid)
            uid_body = uid_norm.replace("roadm ", "").replace("trx ", "").strip()
            if search_term in uid_body or uid_body in search_term:
                candidates.append(uid)
                
    if not candidates:
        # Fallback de búsqueda parcial
        for uid, el in all_elements.items():
            if el["type"] == node_type:
                if search_term in normalize_string(uid):
                    candidates.append(uid)
                    
    if not candidates:
        return None
        
    if len(candidates) == 1:
        return candidates[0]
        
    # Si hay múltiples candidatos, elegir el más cercano al vecino
    if neighbor_node:
        best_cand = None
        best_dist = float('inf')
        for cand in candidates:
            try:
                start_node = cand
                if cand.startswith("trx "):
                    roadm_uid = cand.replace("trx ", "roadm ")
                    if roadm_uid in G:
                        start_node = roadm_uid
                        
                end_node = neighbor_node
                if neighbor_node.startswith("trx "):
                    end_node = neighbor_node.replace("trx ", "roadm ")
                    
                if nx.has_path(G, start_node, end_node):
                    dist = nx.shortest_path_length(G, start_node, end_node, weight="weight")
                    if dist < best_dist:
                        best_dist = dist
                        best_cand = cand
                elif nx.has_path(G, end_node, start_node):
                    dist = nx.shortest_path_length(G, end_node, start_node, weight="weight")
                    if dist < best_dist:
                        best_dist = dist
                        best_cand = cand
            except Exception:
                pass
        if best_cand:
            return best_cand
            
    candidates.sort(key=len)
    return candidates[0]

def calcular_umbral_dinamico(velocidad_gbps, p_rx):
    """Calcula el umbral de OSNR dinámico en base a la velocidad y la potencia de recepción."""
    # Valores por defecto del transceptor si no hay potencia de recepción
    osnr_defaults = {"100": 11.8, "200": 20.5, "300": 20.5, "400": 23.5}
    if p_rx is None or pd.isna(p_rx):
        return osnr_defaults.get(str(int(float(velocidad_gbps))), 23.5)
    
    vel = int(float(velocidad_gbps))
    
    if vel == 400:
        if p_rx >= -14.0:
            return 23.5
        elif p_rx <= -16.0:
            return 25.0
        else:
            return 23.5 + 1.5 * (-14.0 - p_rx) / 2.0
            
    elif vel == 300:
        if p_rx >= -16.0:
            return 20.5
        elif p_rx <= -20.0:
            return 21.5
        else:
            return 20.5 + 1.0 * (-16.0 - p_rx) / 4.0
            
    elif vel == 200:
        if p_rx >= -16.0:
            return 20.5
        elif p_rx <= -18.0:
            return 21.5
        else:
            return 20.5 + 1.0 * (-16.0 - p_rx) / 2.0
            
    elif vel == 100:
        if p_rx >= -20.0:
            return 11.8
        elif p_rx <= -25.0:
            return 12.8
        else:
            return 11.8 + 1.0 * (-20.0 - p_rx) / 5.0
            
    return 23.5

def main():
    print(f"[1/5] Cargando red y equipamientos...")
    with open(NETWORK_JSON) as f:
        network_data = json.load(f)
    all_elements = {e["uid"]: e for e in network_data["elements"]}
    all_connections = network_data["connections"]
    
    G = nx.DiGraph()
    for c in all_connections:
        G.add_edge(c["from_node"], c["to_node"], weight=float(c.get("length", 1)))
        
    print(f"[2/5] Cargando mapa de potencias desde el archivo base...")
    if not os.path.exists(BASE_RESULTADOS):
        print(f"ERROR: No se encontró el archivo base {BASE_RESULTADOS}")
        sys.exit(1)
        
    df_base = pd.read_csv(BASE_RESULTADOS, sep='\t')
    power_map = {}
    for idx, row in df_base.iterrows():
        orig = str(row["Origen"]).strip()
        dest = str(row["Destino"]).strip()
        power_map[(orig, dest)] = float(row["Potencia_Recibida_dBm"]) if not pd.isna(row["Potencia_Recibida_dBm"]) else None

    print(f"[3/5] Leyendo resultados de regeneración {REGEN_RESULTADOS}...")
    if not os.path.exists(REGEN_RESULTADOS):
        print(f"ERROR: No se encontró el archivo de regeneración {REGEN_RESULTADOS}")
        sys.exit(1)
        
    df_regen = pd.read_csv(REGEN_RESULTADOS, sep='\t')
    df_regen = df_regen.dropna(subset=["Origen", "Destino"])
    
    # Inicializar columnas nuevas
    df_regen["Necesito Bajada"] = "NO"
    df_regen["Factible con bajada"] = "SI"
    df_regen["Velocidad_Ajustada [Gbps]"] = df_regen["Velocidad [Gbps]"]
    df_regen["GSNR_Total_dB_Ajustada"] = df_regen["GSNR_Total_dB"]
    df_regen["Umbral_OSNR_dB_Ajustada"] = df_regen["Umbral_OSNR_dB"]
    
    # Procesamos solo las filas que requirieron regeneración originalmente
    # o las que terminaron en Reg_Factible == "NO"
    filas_no_factibles = df_regen[df_regen["Reg_Factible"] == "NO"]
    print(f"[4/5] Encontradas {len(filas_no_factibles)} demandas no factibles con regeneración en el CSV de entrada.")
    
    for idx, row in df_regen.iterrows():
        # Si el enlace es factible de forma directa, o ya es factible con regeneración, no hacemos simulación
        if row["Factible"] == "SI" or row["Reg_Factible"] == "SI":
            continue
            
        origen = str(row["Origen"]).strip()
        destino = str(row["Destino"]).strip()
        orig_speed = float(row["Velocidad [Gbps]"])
        p_rx = power_map.get((origen, destino), None)
        
        # Mapeo y reconstrucción de camino con resolución multipaso para evitar ambigüedades
        ruta_str = str(row["Ruta"]).strip()
        ruta_limpia = " ".join(ruta_str.split())
        if '->' in ruta_limpia:
            ciudades = [c.strip() for c in ruta_limpia.split('->')]
        else:
            ciudades = [c.strip() for c in ruta_limpia.split('-')]
            
        nodos_ruta = [None] * len(ciudades)
        tipos = ["Roadm"] * len(ciudades)
        tipos[0] = "Transceiver"
        tipos[-1] = "Transceiver"
        
        # Paso 1: Resolver nodos con candidato único
        for i, ciudad in enumerate(ciudades):
            search_term = normalize_string(ciudad)
            candidates = []
            for uid, el in all_elements.items():
                if el["type"] == tipos[i]:
                    uid_norm = normalize_string(uid)
                    uid_body = uid_norm.replace("roadm ", "").replace("trx ", "").strip()
                    if search_term in uid_body or uid_body in search_term:
                        candidates.append(uid)
            if not candidates:
                for uid, el in all_elements.items():
                    if el["type"] == tipos[i]:
                        if search_term in normalize_string(uid):
                            candidates.append(uid)
            if len(candidates) == 1:
                nodos_ruta[i] = candidates[0]
                
        # Paso 2: Iterar para resolver nodos ambiguos usando vecinos ya resueltos
        for _ in range(3):
            for i, ciudad in enumerate(ciudades):
                if nodos_ruta[i] is not None:
                    continue
                    
                neighbors = []
                if i > 0 and nodos_ruta[i-1] is not None:
                    neighbors.append(nodos_ruta[i-1])
                if i < len(ciudades) - 1 and nodos_ruta[i+1] is not None:
                    neighbors.append(nodos_ruta[i+1])
                    
                if not neighbors:
                    continue
                    
                search_term = normalize_string(ciudad)
                candidates = []
                for uid, el in all_elements.items():
                    if el["type"] == tipos[i]:
                        uid_norm = normalize_string(uid)
                        uid_body = uid_norm.replace("roadm ", "").replace("trx ", "").strip()
                        if search_term in uid_body or uid_body in search_term:
                            candidates.append(uid)
                if not candidates:
                    for uid, el in all_elements.items():
                        if el["type"] == tipos[i]:
                            if search_term in normalize_string(uid):
                                candidates.append(uid)
                if not candidates:
                    continue
                    
                best_cand = None
                best_dist = float('inf')
                for cand in candidates:
                    start_node = cand.replace("trx ", "roadm ") if cand.startswith("trx ") else cand
                    dist_sum = 0
                    reachable_count = 0
                    for neb in neighbors:
                        end_node = neb.replace("trx ", "roadm ") if neb.startswith("trx ") else neb
                        try:
                            if nx.has_path(G, start_node, end_node):
                                dist_sum += nx.shortest_path_length(G, start_node, end_node, weight="weight")
                                reachable_count += 1
                            elif nx.has_path(G, end_node, start_node):
                                dist_sum += nx.shortest_path_length(G, end_node, start_node, weight="weight")
                                reachable_count += 1
                        except Exception:
                            pass
                    if reachable_count > 0:
                        avg_dist = dist_sum / reachable_count
                        if avg_dist < best_dist:
                            best_dist = avg_dist
                            best_cand = cand
                if best_cand:
                    nodos_ruta[i] = best_cand
                    
        # Paso 3: Fallback final para los que sigan sin resolverse
        for i, ciudad in enumerate(ciudades):
            if nodos_ruta[i] is None:
                nodos_ruta[i] = find_node_for_city(ciudad, tipos[i], all_elements, G)
                
        if None in nodos_ruta:
            print(f"  [!] Error de mapeo para {origen} -> {destino}. Ignorando fila.")
            continue
            
        try:
            full_path = []
            for i in range(len(nodos_ruta) - 1):
                u = nodos_ruta[i]
                v = nodos_ruta[i+1]
                sub_path = nx.shortest_path(G, u, v, weight="weight")
                if i == 0:
                    full_path.extend(sub_path)
                else:
                    full_path.extend(sub_path[1:])
        except nx.NetworkXNoPath:
            print(f"  [!] No hay camino físico entre {origen} y {destino}")
            continue
            
        # Re-evaluar regeneración a la velocidad original con el mapeo corregido
        target_osnr = calcular_umbral_dinamico(orig_speed, p_rx)
        reg_count, reg_nodes, reg_gsnrs, reg_ok = optimize_regeneration(full_path, target_osnr, all_elements, all_connections)
        
        if reg_ok:
            # Era un caso skipped por el bug de software. Ahora funciona con la velocidad original!
            print(f"  [✓] Enlace corregido: {origen} -> {destino} es FACTIBLE con regeneración a velocidad original ({int(orig_speed)}G).")
            df_regen.at[idx, "Reg_Factible"] = "SI"
            df_regen.at[idx, "Reg_Count"] = reg_count
            
            # Reconstruir Ruta_Regenerada para actualizar el CSV
            roadms_in_path = [clean(n) for n in full_path if all_elements[n]["type"] == "Roadm"]
            gsnr_map = {}
            current_source = reg_nodes[0]
            for node in roadms_in_path:
                if node == reg_nodes[0]:
                    continue
                is_reg = (node in reg_nodes[1:-1])
                val = run_gnpy_on_path(full_path, f"trx {current_source}", f"trx {node}", all_elements, all_connections)
                gsnr_map[node] = f"{val:.2f} dB" if val is not None else "N/A"
                if is_reg or node == reg_nodes[-1]:
                    current_source = node
                    
            ruta_partes = []
            for i, node in enumerate(roadms_in_path):
                node_display = node
                if node in gsnr_map:
                    node_display = f"{node} ({gsnr_map[node]})"
                if i > 0:
                    prev_node = roadms_in_path[i-1]
                    is_prev_reg = (prev_node in reg_nodes[1:-1])
                    sep = " [REG]-> " if is_prev_reg else " -> "
                    ruta_partes.append(sep + node_display)
                else:
                    ruta_partes.append(node_display)
            df_regen.at[idx, "Ruta_Regenerada"] = "".join(ruta_partes)
            df_regen.at[idx, "Nodos_Regeneradores"] = " - ".join(reg_nodes[1:-1]) if len(reg_nodes) > 2 else ""
            
            # No necesita bajada
            df_regen.at[idx, "Necesito Bajada"] = "NO"
            df_regen.at[idx, "Factible con bajada"] = "SI"
            df_regen.at[idx, "Velocidad_Ajustada [Gbps]"] = orig_speed
            df_regen.at[idx, "GSNR_Total_dB_Ajustada"] = row["GSNR_Total_dB"]
            df_regen.at[idx, "Umbral_OSNR_dB_Ajustada"] = target_osnr
        else:
            # Enlace realmente no factible. Procedemos con la bajada de velocidad
            print(f"  [i] Enlace {origen} -> {destino} requiere bajada de velocidad. Iniciando step-down...")
            df_regen.at[idx, "Necesito Bajada"] = "SI"
            
            # Asegurar que las columnas originales de regeneración muestren que no es factible a la velocidad original
            df_regen.at[idx, "Reg_Factible"] = "NO"
            df_regen.at[idx, "Reg_Count"] = 0
            df_regen.at[idx, "Ruta_Regenerada"] = ""
            df_regen.at[idx, "Nodos_Regeneradores"] = ""
            
            speeds = [400.0, 300.0, 200.0, 100.0]
            try:
                curr_idx = speeds.index(float(orig_speed))
            except ValueError:
                curr_idx = 0
                
            found_feasible = False
            for speed in speeds[curr_idx+1:]:
                print(f"      Evaluando a {int(speed)} Gbps...")
                target_osnr_lower = calcular_umbral_dinamico(speed, p_rx)
                reg_count_l, reg_nodes_l, reg_gsnrs_l, reg_ok_l = optimize_regeneration(full_path, target_osnr_lower, all_elements, all_connections)
                
                if reg_ok_l:
                    print(f"      -> ¡Factible a {int(speed)} Gbps con {reg_count_l} regeneradores!")
                    df_regen.at[idx, "Factible con bajada"] = "SI"
                    df_regen.at[idx, "Velocidad_Ajustada [Gbps]"] = speed
                    df_regen.at[idx, "GSNR_Total_dB_Ajustada"] = row["GSNR_Total_dB"]
                    df_regen.at[idx, "Umbral_OSNR_dB_Ajustada"] = target_osnr_lower
                    found_feasible = True
                    break
            
            if not found_feasible:
                print(f"      -> [!] No es factible a ninguna velocidad permitida.")
                df_regen.at[idx, "Factible con bajada"] = "NO"
                df_regen.at[idx, "Velocidad_Ajustada [Gbps]"] = 100.0 # Velocidad mínima
                df_regen.at[idx, "GSNR_Total_dB_Ajustada"] = row["GSNR_Total_dB"]
                df_regen.at[idx, "Umbral_OSNR_dB_Ajustada"] = calcular_umbral_dinamico(100.0, p_rx)

    print(f"[5/5] Escribiendo el archivo formateado en {OUTPUT_CSV}...")
    headers = [
        "Region", "Origen", "Destino", "Cantidad de Enlaces", "Velocidad [Gbps]",
        "Ruta", "Distancia_km", "GSNR_Total_dB", "Umbral_OSNR_dB", "Factible",
        "Necesito_Regeneracion", "Reg_Factible", "Reg_Count", "Ruta_Regenerada", "Nodos_Regeneradores",
        "Necesito Bajada", "Factible con bajada", "Velocidad_Ajustada [Gbps]", "GSNR_Total_dB", "Umbral_OSNR_dB"
    ]
    
    # Columnas correspondientes de df_regen en orden
    df_columns_order = [
        "Region", "Origen", "Destino", "Cantidad de Enlaces", "Velocidad [Gbps]",
        "Ruta", "Distancia_km", "GSNR_Total_dB", "Umbral_OSNR_dB", "Factible",
        "Necesito_Regeneracion", "Reg_Factible", "Reg_Count", "Ruta_Regenerada", "Nodos_Regeneradores",
        "Necesito Bajada", "Factible con bajada", "Velocidad_Ajustada [Gbps]", "GSNR_Total_dB_Ajustada", "Umbral_OSNR_dB_Ajustada"
    ]
    
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f_out:
        # Escribir cabecera citada con tabulaciones
        quoted_headers = [f'"{h}"' for h in headers]
        f_out.write("\t".join(quoted_headers) + "\n")
        
        # Escribir cada fila respetando el formato del original
        for idx, row in df_regen.iterrows():
            row_vals = []
            for col in df_columns_order:
                val = row[col]
                if pd.isna(val) or val == "" or val is None:
                    row_vals.append("")
                else:
                    if isinstance(val, float):
                        if val.is_integer():
                            val_str = str(int(val))
                        else:
                            val_str = f"{val:.2f}" if col in ["GSNR_Total_dB", "Umbral_OSNR_dB", "GSNR_Total_dB_Ajustada", "Umbral_OSNR_dB_Ajustada"] else str(val)
                    else:
                        val_str = str(val)
                    # Quitar comillas si ya existen para evitar duplicación
                    val_str = val_str.replace('"', '')
                    row_vals.append(f'"{val_str}"')
            f_out.write("\t".join(row_vals) + "\n")
            
    print("¡Finalizado con éxito!")

if __name__ == "__main__":
    main()
