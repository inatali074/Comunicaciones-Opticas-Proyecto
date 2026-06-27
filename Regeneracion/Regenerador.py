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
venv_site = os.path.join(sys.prefix, 'lib', 'python3.12', 'site-packages')
if venv_site not in sys.path:
    sys.path.append(venv_site)

from gnpy.tools.cli_examples import transmission_main_example

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NETWORK_JSON = os.path.join(SCRIPT_DIR, "..", "Consigna", "network_mashe.json")
EQUIPMENT_JSON = os.path.join(SCRIPT_DIR, "..", "Consigna", "equipament_real_marcos_corregido.json")
INPUT_CSV = os.path.join(SCRIPT_DIR, "..", "resultados_gsnr_demandas_base.csv")
OUTPUT_CSV = os.path.join(SCRIPT_DIR, "resultados_gsnr_demandas_base_regenerado.csv")

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
        trxs_in_trim = [e["uid"] for e in network_trimmed["elements"] if e["type"] == "Transceiver"]
        print(f"      TRXs in network_trimmed: {trxs_in_trim}")
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

def main():
    print(f"[1/4] Cargando {NETWORK_JSON} y {EQUIPMENT_JSON}...")
    with open(NETWORK_JSON) as f:
        network_data = json.load(f)
    
    all_elements = {e["uid"]: e for e in network_data["elements"]}
    all_connections = network_data["connections"]
    
    # Construir grafo para obtener rutas físicas
    G = nx.DiGraph()
    for c in all_connections:
        G.add_edge(c["from_node"], c["to_node"], weight=float(c.get("length", 1)))

    print(f"[2/4] Leyendo {INPUT_CSV}...")
    with open(INPUT_CSV, 'r', encoding='utf-8') as f_check:
        first_line = f_check.readline()
        sep = '\t' if '\t' in first_line else ','
    df = pd.read_csv(INPUT_CSV, sep=sep)
    
    # Preparar nuevas columnas
    df["Necesito_Regeneracion"] = "NO"
    df["Reg_Factible"] = ""
    df["Reg_Count"] = 0
    df["Ruta_Regenerada"] = ""
    df["Nodos_Regeneradores"] = ""

    # Filtrar solo los enlaces no factibles
    no_factibles = df[df["Factible"] == "NO"]
    print(f"[3/4] Encontrados {len(no_factibles)} enlaces no factibles. Iniciando evaluación...")
    
    for idx, row in no_factibles.iterrows():
        origen = str(row["Origen"]).strip()
        destino = str(row["Destino"]).strip()
        target_osnr = float(row["Umbral_OSNR_dB"])
        
        src_trx = f"trx {origen}"
        dst_trx = f"trx {destino}"
        
        # Validación
        if src_trx not in all_elements or dst_trx not in all_elements:
            print(f"  [!] TRX no encontrado para {origen} -> {destino}")
            df.at[idx, "Necesito_Regeneracion"] = "SI"
            df.at[idx, "Reg_Factible"] = "NO"
            continue
        
        # Reconstruir el camino físico original siguiendo la columna 'Ruta' de las demandas base
        ruta_str = str(row["Ruta"]).strip()
        ruta_limpia = " ".join(ruta_str.split())
        if '->' in ruta_limpia:
            ciudades = [c.strip() for c in ruta_limpia.split('->')]
        else:
            ciudades = [c.strip() for c in ruta_limpia.split('-')]
            
        nodos_ruta = []
        map_error = False
        for i, ciudad in enumerate(ciudades):
            ciudad_str = ciudad.strip()
            if i == 0:
                nodos_ruta.append(src_trx)
            elif i == len(ciudades) - 1:
                nodos_ruta.append(dst_trx)
            else:
                candidates = [uid for uid in all_elements if uid.startswith("roadm") and ciudad_str.lower() in uid.lower()]
                if len(candidates) == 1:
                    nodos_ruta.append(candidates[0])
                elif len(candidates) > 1:
                    prev = nodos_ruta[-1]
                    best_cand = None
                    best_dist = float('inf')
                    for cand in candidates:
                        try:
                            if nx.has_path(G, prev, cand):
                                dist = nx.shortest_path_length(G, prev, cand, weight="weight")
                                if dist < best_dist:
                                    best_dist = dist
                                    best_cand = cand
                        except nx.NetworkXNoPath:
                            pass
                    nodos_ruta.append(best_cand if best_cand else candidates[0])
                else:
                    print(f"  [!] ROADM no encontrado para la ciudad intermedia '{ciudad_str}' en la ruta de {origen} -> {destino}")
                    map_error = True
                    break
        
        if map_error:
            df.at[idx, "Necesito_Regeneracion"] = "SI"
            df.at[idx, "Reg_Factible"] = "NO"
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
            print(f"  [!] No hay camino físico entre {origen} y {destino} siguiendo la ruta '{ruta_str}'")
            df.at[idx, "Necesito_Regeneracion"] = "SI"
            df.at[idx, "Reg_Factible"] = "NO"
            continue
            
        print(f"  -> Evaluando regeneración para: {origen} a {destino} (Umbral OSNR: {target_osnr} dB)")
        
        # Calcular optimización de regeneración
        reg_count, reg_nodes, reg_gsnrs, reg_ok = optimize_regeneration(full_path, target_osnr, all_elements, all_connections)
        
        reg_factible = reg_ok and (reg_count <= 4)
        
        df.at[idx, "Necesito_Regeneracion"] = "SI"
        df.at[idx, "Reg_Factible"] = "SI" if reg_factible else "NO"
        df.at[idx, "Reg_Count"] = max(0, reg_count) if reg_factible else 0
        
        # Obtener todos los ROADMs en la ruta completa
        roadms_in_path = [
            clean(n) for n in full_path
            if all_elements[n]["type"] == "Roadm"
        ]
        
        # Mapear cada ROADM intermedio o de destino a su GSNR correspondiente
        gsnr_map = {}
        if reg_factible:
            current_source = reg_nodes[0]
            for node in roadms_in_path:
                if node == reg_nodes[0]:
                    continue
                is_reg = (node in reg_nodes[1:-1])
                val = run_gnpy_on_path(
                    full_path,
                    f"trx {current_source}",
                    f"trx {node}",
                    all_elements,
                    all_connections
                )
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
                is_prev_reg = (prev_node in reg_nodes[1:-1]) if reg_factible else False
                sep = " [REG]-> " if is_prev_reg else " -> "
                ruta_partes.append(sep + node_display)
            else:
                ruta_partes.append(node_display)
        df.at[idx, "Ruta_Regenerada"] = "".join(ruta_partes) if reg_factible else ""
        if reg_factible and len(reg_nodes) > 2:
            df.at[idx, "Nodos_Regeneradores"] = " - ".join(reg_nodes[1:-1])
        
    print(f"[4/4] Guardando resultados en {OUTPUT_CSV}...")
    df.to_csv(OUTPUT_CSV, sep='\t', index=False)
    print("¡Proceso completado con éxito!")

if __name__ == "__main__":
    main()
