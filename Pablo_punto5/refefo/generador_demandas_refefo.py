import json
import random
import networkx as nx
import os
import sys
import copy
import math
import pandas as pd

# ==========================================================
# CONFIGURACIÓN
# ==========================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NETWORK_JSON = os.path.join(SCRIPT_DIR, "..", "..", "Consigna", "network_mashe.json")
EQUIPMENT_JSON = os.path.join(SCRIPT_DIR, "..", "..", "Consigna", "equipament_real_marcos_corregido.json")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "demandas_refefo.csv")

K_PATHS = 5
ITERATIONS = 200
SAVE_EVERY = 20
PENALIDAD_DISJOINT = 500.0


# ==========================================================
# UTILIDADES
# ==========================================================

def clean(name):
    """Limpia nombres para visualización y CSV."""
    return str(name).replace("roadm ", "").replace("trx ", "").strip()


def clean_path(path_list):
    """Filtra la secuencia para mostrar solo nodos lógicos."""
    cleaned = []
    for n in path_list:
        if any(x in n.lower() for x in ["fiber", "edfa", "span"]):
            continue
        name = clean(n)
        if not cleaned or cleaned[-1] != name:
            cleaned.append(name)
    return cleaned


# ==========================================================
# RESUME EFICIENTE
# ==========================================================

def get_last_iteration(file):
    """Determina la última iteración sin cargar el archivo completo."""
    if not os.path.exists(file):
        return 0
    try:
        with open(file, 'rb') as f:
            f.seek(0, os.SEEK_END)
            if f.tell() < 100: return 0
            f.seek(-2048, os.SEEK_END)
            lines = f.readlines()
            last_line = lines[-1].decode().strip()
            return int(last_line.split(",")[0])
    except Exception:
        return 0


# ==========================================================
# MOTOR DE ESTIMACIÓN ANALÍTICA DE GSNR (SIN GNPy)
# ==========================================================

def run_gsnr_on_path_analytical(path, mode, all_elements, equipment_data):
    """Calcula la GSNR total de forma analítica emulando la física de GNPy."""
    try:
        fiber_eq = equipment_data.get("Fiber", [{}])[0]
    except Exception:
        fiber_eq = {}
    dispersion_si = fiber_eq.get("dispersion", 1.8e-5)
    A_eff_m2 = fiber_eq.get("effective_area", 80e-12)
    n2_m2_W = 2.6e-20 
    gamma_1_W_km = (2 * math.pi * n2_m2_W) / (1550e-9 * A_eff_m2) * 1e3

    try:
        roadm_eq = equipment_data.get("Roadm", [{}])[0]
    except Exception:
        roadm_eq = {}
    target_pch_out = roadm_eq.get("target_pch_out_db", -20)

    try:
        si_eq = equipment_data.get("SI", [{}])[0]
    except Exception:
        si_eq = {}
    f_min = si_eq.get("f_min", 191.3e12)
    f_max = si_eq.get("f_max", 196.1e12)
    spacing = si_eq.get("spacing", 50e9)
    N_ch = int((f_max - f_min) / spacing) if spacing > 0 else 96
    B_ref = 12.5e9
    const_ase = 10 * math.log10(6.626e-34 * 193.5e12 * B_ref * 1e3)

    baud_rate = mode.get("baud_rate", 31.6e9)
    tx_osnr = mode.get("tx_osnr", 38.0)

    p_in_current = target_pch_out
    osnri_inv_sum = 0.0
    
    lambda_ = 1550e-9
    c = 299792458
    beta2 = (lambda_**2 / (2 * math.pi * c)) * dispersion_si
    
    inv_gsnr_nli = 0.0
    N_s = 0
    
    for i in range(len(path)):
        node_uid = path[i]
        if node_uid not in all_elements:
            continue
        node = all_elements[node_uid]
        t = node["type"]
        
        if t == "Edfa":
            gain = node.get("gain_target", 0)
            if gain == 0:
                uid_lower = node['uid'].lower()
                if "booster" in uid_lower:
                    gain = 18.0
                else:
                    last_loss = 20.0
                    if i > 0:
                        prev_node_uid = path[i-1]
                        if prev_node_uid in all_elements:
                            prev_node = all_elements[prev_node_uid]
                            if prev_node["type"] == "Fiber":
                                p_length = prev_node.get("length", prev_node.get("params", {}).get("length", 0))
                                p_loss_coef = prev_node.get("loss_coef", prev_node.get("params", {}).get("loss_coef", 0.2))
                                last_loss = p_length * p_loss_coef + 0.5
                    gain = last_loss
            
            nf = 5.5
            osnr_i = p_in_current - nf - const_ase
            osnri_inv_sum += 10**(-osnr_i/10)
            p_in_current += gain
            
        elif t == "Fiber":
            length = node.get("length", node.get("params", {}).get("length", 0))
            loss_coef = node.get("loss_coef", node.get("params", {}).get("loss_coef", 0.2))
            alpha_lin = (loss_coef * math.log(10)) / 10
            
            P_launch_w = 10**(p_in_current/10) * 1e-3
            
            if length > 0 and alpha_lin > 0:
                L_eff = (1 - math.exp(-alpha_lin * length)) / alpha_lin
                L_eff_m = L_eff * 1000.0
                N_s += 1
                
                try:
                    argument_log = math.pi**2 * beta2 * L_eff_m * (N_ch**2) * (baud_rate**2)
                    log_term = math.log(abs(argument_log))
                    denominator = math.pi * beta2 * (baud_rate**3)
                    gamma_m = gamma_1_W_km * 1e-3
                    front_term_span = ((2/3)**3) * (gamma_m**2) * L_eff_m * (P_launch_w**2)
                    inv_gsnr_nli_span = front_term_span * (log_term / denominator) * B_ref
                    inv_gsnr_nli += inv_gsnr_nli_span
                except Exception:
                    pass
                
            loss = (length * loss_coef) + 0.5
            p_in_current -= loss
            
        elif t == "Roadm":
            p_in_current = target_pch_out
            
    if N_s == 0:
        return None
        
    inv_gsnr_red = osnri_inv_sum + inv_gsnr_nli
    inv_tx = 10**(-tx_osnr/10)
    inv_gsnr_total = inv_tx + inv_gsnr_red
    
    gsnr_total_db = -10 * math.log10(inv_gsnr_total) if inv_gsnr_total > 0 else float('inf')
    return gsnr_total_db


# ==========================================================
# REGENERACIÓN Y RUTAS
# ==========================================================

def optimize_regeneration(full_path, target_osnr, all_elements, all_connections, mode, equipment_data):
    """Calcula la ubicación de regeneradores si la señal es insuficiente."""
    roadms_trx = [
        n for n in full_path
        if all_elements[n]["type"] == "Roadm" and f"trx {clean(n)}" in all_elements
    ]

    if len(roadms_trx) < 2:
        return 0, [], False

    current_idx = 0
    reg_nodes = [clean(roadms_trx[0])]
    path_possible = True

    while current_idx < len(roadms_trx) - 1:
        best_idx = None
        for next_idx in range(len(roadms_trx) - 1, current_idx, -1):
            # Obtener el sub-camino entre roadms_trx[current_idx] y roadms_trx[next_idx]
            # para calcular su GSNR analítica
            start_node = roadms_trx[current_idx]
            end_node = roadms_trx[next_idx]
            
            # Extraer sub-camino indexado
            idx_start = full_path.index(start_node)
            idx_end = full_path.index(end_node)
            sub_path = full_path[idx_start:idx_end+1]
            
            gsnr = run_gsnr_on_path_analytical(
                sub_path,
                mode,
                all_elements,
                equipment_data
            )
            if gsnr is not None and gsnr >= target_osnr:
                best_idx = next_idx
                break

        if best_idx is None:
            path_possible = False
            best_idx = current_idx + 1

        reg_nodes.append(clean(roadms_trx[best_idx]))
        current_idx = best_idx

    return len(reg_nodes) - 2, reg_nodes, path_possible


def k_shortest_paths_incremental(G_original, source, target, K=5):
    """Encuentra K caminos disjuntos mediante penalización de aristas."""
    G = G_original.copy()
    paths = []
    seen = set()

    for _ in range(K):
        try:
            path = nx.shortest_path(G, source, target, weight="weight")
        except nx.NetworkXNoPath:
            break

        t = tuple(path)
        if t in seen: break
        paths.append(path)
        seen.add(t)

        for u, v in zip(path[:-1], path[1:]):
            if G.has_edge(u, v):
                G[u][v]["weight"] += PENALIDAD_DISJOINT
    return paths


# ==========================================================
# GUARDADO APPEND-ONLY
# ==========================================================

def save_batch(rows):
    """Agrega datos al CSV de forma eficiente."""
    if not rows: return
    df = pd.DataFrame(rows)
    file_exists = os.path.isfile(OUTPUT_FILE)
    df.to_csv(OUTPUT_FILE, mode='a', index=False, header=not file_exists)
    print(f"[I/O] +{len(rows)} filas añadidas al dataset.")


# ==========================================================
# MAIN
# ==========================================================

def main():
    start_iter = get_last_iteration(OUTPUT_FILE) + 1
    print(f"[SISTEMA] Iniciando desde iteración: {start_iter}")

    if not os.path.exists(NETWORK_JSON):
        print(f"ERROR: No se encontró el archivo de red {NETWORK_JSON}")
        sys.exit(1)
    if not os.path.exists(EQUIPMENT_JSON):
        print(f"ERROR: No se encontró el archivo de equipos {EQUIPMENT_JSON}")
        sys.exit(1)

    with open(NETWORK_JSON) as f:
        network_data = json.load(f)
    with open(EQUIPMENT_JSON) as f:
        equipment_data = json.load(f)

    all_elements = {e["uid"]: e for e in network_data["elements"]}
    all_connections = network_data["connections"]
    trx_modes = equipment_data["Transceiver"][0]["mode"]

    G = nx.DiGraph()
    for c in all_connections:
        G.add_edge(c["from_node"], c["to_node"], weight=float(c.get("length", 1)))

    trx_nodes = [e["uid"] for e in network_data["elements"] if e["uid"].startswith("trx ")]
    all_locations = sorted(set(clean_path(list(all_elements.keys()))))

    buffer_rows = []

    for iter_idx in range(start_iter, start_iter + ITERATIONS):
        src_trx, dst_trx = random.sample(trx_nodes, 2)

        # Selección dinámica de modo de transmisión
        weights = [m.get("probability", 1.0) for m in trx_modes] if "probability" in trx_modes[0] else [1.0]*len(trx_modes)
        mode = random.choices(trx_modes, weights=weights, k=1)[0]

        target_osnr = mode["OSNR"]
        bitrate = round(mode["bit_rate"] / 1e9, 2)

        print(f"[{iter_idx}] {clean(src_trx)} - {clean(dst_trx)} | {bitrate}G")
        paths = k_shortest_paths_incremental(G, src_trx, dst_trx, K=K_PATHS)

        for k_idx, path in enumerate(paths):
            clean_p = clean_path(path)
            gsnr_direct = run_gsnr_on_path_analytical(path, mode, all_elements, equipment_data)
            direct_ok = (gsnr_direct is not None) and (gsnr_direct >= target_osnr)

            reg_count, reg_nodes, reg_ok = 0, [], False
            path_reg_final = " - ".join(clean_p)

            if not direct_ok:
                reg_count, reg_nodes, reg_ok = optimize_regeneration(
                    path, target_osnr, all_elements, all_connections, mode, equipment_data
                )
                path_reg_final = " - ".join(reg_nodes)

            row = {
                "Iteración": iter_idx,
                "Source": clean(src_trx),
                "Destination": clean(dst_trx),
                "Gbps": bitrate,
                "K_Path": k_idx + 1,
                "GSNR_Direct": gsnr_direct,
                "Direct_Feasible": direct_ok,
                "Reg_Feasible": reg_ok,
                "Reg_Count": reg_count if not direct_ok else 0,
                "Path_Reg": path_reg_final,
                "Path_Sequence": " - ".join(clean_p)
            }

            for loc in all_locations:
                row[f"Node_{loc}"] = 1 if loc in clean_p else 0
            buffer_rows.append(row)

        if iter_idx % SAVE_EVERY == 0:
            save_batch(buffer_rows)
            buffer_rows = []

    save_batch(buffer_rows)
    print("FIN: Proceso completado.")


if __name__ == "__main__":
    main()
