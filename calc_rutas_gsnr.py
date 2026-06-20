import json
import csv
import math
import os

def load_json(filepath):
    if not os.path.exists(filepath):
        print(f"ERROR: No se encontró el archivo {filepath}")
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# Archivos con fallback a la carpeta Consigna/
NETWORK_FILE = 'network_mashe.json' if os.path.exists('network_mashe.json') else 'Consigna/network_mashe.json'
EQUIPMENT_FILE = 'equipament_real_marcos_corregido.json' if os.path.exists('equipament_real_marcos_corregido.json') else 'Consigna/equipament_real_marcos_corregido.json'
DEMANDAS_FILE = 'Demanda_Base - Tráfico base.csv' if os.path.exists('Demanda_Base - Tráfico base.csv') else 'Consigna/Demanda_Base - Tráfico base.csv'
RESULTADOS_FILE = 'resultados_gsnr_demandas_base.csv'

network_data = load_json(NETWORK_FILE)
equipment_data = load_json(EQUIPMENT_FILE)

if not network_data or not equipment_data:
    exit(1)

print("--- Extrayendo parámetros de equipos reales ---")

# 1. Buscar Fibra
fiber_eq = equipment_data.get("Fiber", [{}])[0]
if not fiber_eq:
    print("ADVERTENCIA: No se encontró fibra en equipaments_real.json. Usando valores genéricos.")

# GNPy almacena dispersion en s/m^2. 1.8e-5 s/m^2 = 18.0 ps/nm/km
dispersion_si = fiber_eq.get("dispersion", 1.8e-5)
D_ps_nm_km = dispersion_si * 1e6 
A_eff_m2 = fiber_eq.get("effective_area", 8.5e-11)
# n2 típico para sílice (Corning SMF-28)
n2_m2_W = 2.6e-20 
gamma_1_W_km = (2 * math.pi * n2_m2_W) / (1550e-9 * A_eff_m2) * 1e3

print(f"Fibra: D = {D_ps_nm_km:.2f} ps/nm/km, A_eff = {A_eff_m2:.1e} m^2, n2 = {n2_m2_W:.2e} m^2/W, gamma = {gamma_1_W_km:.2f} 1/W*km")

# 2. Buscar ROADM
roadm_eq = equipment_data.get("Roadm", [{}])[0]
if not roadm_eq:
    print("ADVERTENCIA: No se encontró ROADM.")
target_pch_out = roadm_eq.get("target_pch_out_db", -20)
roadm_pdl = roadm_eq.get("pdl", 1.5)

print(f"ROADM: target_pch_out = {target_pch_out} dBm, PDL = {roadm_pdl} dB")

# 3. Buscar Transceiver 400G
trx_eq = equipment_data.get("Transceiver", [{}])[0]
mode_400g = next((m for m in trx_eq.get("mode", []) if "400 Gbit/s" in m.get("format", "")), None)
if not mode_400g:
    print("ADVERTENCIA: No se encontró modo 400G en el Transceiver.")
    mode_400g = {}

baud_rate = mode_400g.get("baud_rate", 63.1e9)
tx_osnr = mode_400g.get("tx_osnr", 38.0)

osnr_req_dict = {
    "100": next((m.get("OSNR", 14.0) for m in trx_eq.get("mode", []) if "100 Gbit/s" in m.get("format", "")), 14.0),
    "200": next((m.get("OSNR", 18.0) for m in trx_eq.get("mode", []) if "200 Gbit/s" in m.get("format", "")), 18.0),
    "300": next((m.get("OSNR", 21.0) for m in trx_eq.get("mode", []) if "300 Gbit/s" in m.get("format", "")), 21.0),
    "400": next((m.get("OSNR", 23.5) for m in trx_eq.get("mode", []) if "400 Gbit/s" in m.get("format", "")), 23.5)
}

print(f"Transceiver: OSNR Reqs: 100G={osnr_req_dict['100']}, 200G={osnr_req_dict['200']}, 300G={osnr_req_dict['300']}, 400G={osnr_req_dict['400']}")

# 4. Parámetros Globales (SI)
si_eq = equipment_data.get("SI", [{}])[0]
f_min = si_eq.get("f_min", 191.35e12)
f_max = si_eq.get("f_max", 196.10e12)
spacing = si_eq.get("spacing", 100e9)
N_ch = int((f_max - f_min) / spacing)
sys_margins = si_eq.get("sys_margins", 2.0)
B_ref = 12.5e9
const_ase = 10 * math.log10(6.626e-34 * 193.5e12 * B_ref * 1e3)

print(f"Sistema: Canales (N_ch) = {N_ch}, Margen = {sys_margins} dB")
print("-----------------------------------------------")

# Diccionario de EDFAs para obtener NF
edfa_dict = {e["type_variety"]: e for e in equipment_data.get("Edfa", [])}

# Parsear la topología del network.json
elements = {e["uid"]: e for e in network_data.get("elements", [])}
connections = network_data.get("connections", [])

adj = {uid: [] for uid in elements}
for conn in connections:
    u = conn["from_node"]
    v = conn["to_node"]
    if u in adj:
        adj[u].append(v)

def bfs_shortest_path(start, end):
    queue = [[start]]
    visited = set([start])
    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node == end:
            return path
        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
    return None

def calcular_ruta(ciudades, velocidad_gbps):
    print(f"\nCalculando ruta: {' -> '.join(ciudades)} a {velocidad_gbps} Gbps")
    vel_key = str(int(float(velocidad_gbps)))
    osnr_req = osnr_req_dict.get(vel_key, 23.5)
    
    # 1. Mapear ciudades a nodos ROADM
    nodos_ruta = []
    for ciudad in ciudades:
        ciudad_str = ciudad.strip()
        candidates = [k for k in elements if (k.startswith("roadm") or "edfa" in k.lower() or "ila" in k.lower()) and ciudad_str.lower() in k.lower()]
        if not candidates:
            print(f"ERROR: No se encontró el nodo para la ciudad '{ciudad_str}'. Saltando ruta.")
            return None
            
        if len(candidates) == 1:
            uid = candidates[0]
        else:
            uid = None
            if nodos_ruta:
                prev = nodos_ruta[-1]
                best_cand = None
                best_dist = float('inf')
                for cand in candidates:
                    p = bfs_shortest_path(prev, cand)
                    if p:
                        dist = len(p)
                        if not cand.startswith("roadm"):
                            dist += 20 # Penalty to prefer ROADMs if distances are similar
                        if dist < best_dist:
                            best_dist = dist
                            best_cand = cand
                uid = best_cand if best_cand else candidates[0]
            else:
                if len(ciudades) > 1:
                    next_ciudad = ciudades[1].strip()
                    next_candidates = [k for k in elements if (k.startswith("roadm") or "edfa" in k.lower() or "ila" in k.lower()) and next_ciudad.lower() in k.lower()]
                    if next_candidates:
                        best_cand = None
                        best_dist = float('inf')
                        for cand in candidates:
                            for n_cand in next_candidates:
                                p = bfs_shortest_path(cand, n_cand)
                                if p:
                                    dist = len(p)
                                    if not cand.startswith("roadm"):
                                        dist += 20
                                    if dist < best_dist:
                                        best_dist = dist
                                        best_cand = cand
                        if best_cand:
                            uid = best_cand
                
                if not uid:
                    exact = f"roadm {ciudad_str}"
                    if exact in candidates:
                        uid = exact
                    else:
                        roadms = [c for c in candidates if c.startswith("roadm")]
                        if roadms:
                            roadms.sort(key=len)
                            uid = roadms[0]
                        else:
                            candidates.sort(key=len)
                            uid = candidates[0]
        nodos_ruta.append(uid)
        
    # 2. Encontrar el camino completo empalmando cada segmento
    camino_completo = []
    for i in range(len(nodos_ruta)-1):
        origen = nodos_ruta[i]
        destino = nodos_ruta[i+1]
        sub_path = bfs_shortest_path(origen, destino)
        if not sub_path:
            print(f"ERROR: No hay camino en network.json entre {origen} y {destino}.")
            return
        
        if i == 0:
            camino_completo.extend(sub_path)
        else:
            camino_completo.extend(sub_path[1:]) # no duplicar el nodo intermedio
            
    # 3. Evaluar el camino
    p_in_current = target_pch_out
    osnri_inv_sum = 0.0
    
    lambda_ = 1550e-9
    c = 299792458
    beta2 = (lambda_**2 / (2 * math.pi * c)) * (D_ps_nm_km * 1e-3)
    P_tx_w = 10**(target_pch_out/10) * 1e-3 # Asumimos P_tx inicial al salir del ROADM/Booster (esto se ajustará tras el booster)
    
    # Acumuladores de NLI
    L_effs = []
    N_s = 0
    total_length = 0.0
    
    for i in range(len(camino_completo)):
        node = elements[camino_completo[i]]
        t = node["type"]
        
        if t == "Edfa":
            # Calcular ganancia y NF
            # Si no hay ganancia exacta usamos el target
            gain = node.get("gain_target", 0)
            
            # Lógica para extraer ganancia según gain_target.jpeg si falta en el JSON
            if gain == 0:
                uid_lower = node['uid'].lower()
                if "booster" in uid_lower:
                    gain = 18.0  # Rango BA: 8 ~ 18 dB, seteamos el máximo típico de salida
                    # print(f"  [INFO] EDFA Booster sin ganancia ({node['uid']}). Asignando {gain} dB (según datasheet OA1825/1835 BA).")
                else:
                    # Para Preamp o In-Line (LA), el rango es 15 ~ 25 dB.
                    # Idealmente compensa la pérdida del span anterior, si no asume un valor medio.
                    # Calculamos la pérdida del último span si existe
                    last_loss = 20.0
                    if len(camino_completo[:i]) > 1:
                        prev_node = elements[camino_completo[i-1]]
                        if prev_node["type"] == "Fiber":
                            p_length = prev_node.get("length", prev_node.get("params", {}).get("length", 0))
                            p_loss_coef = prev_node.get("loss_coef", prev_node.get("params", {}).get("loss_coef", 0.2))
                            last_loss = p_length * p_loss_coef
                    
                    # Clampeamos la pérdida al rango del equipo (15 a 25 dB)
                    gain = max(15.0, min(25.0, last_loss))
                    # print(f"  [INFO] EDFA Preamp/LA sin ganancia ({node['uid']}). Asignando {gain:.1f} dB (rango 15-25 dB compensando span).")
            
            # Buscar la variedad para sacar NF
            variety = node.get("type_variety", "")
            nf = 5.5 # Valor realista de operación (alineado con GNPy)
            # if variety in edfa_dict:
            #     nf = edfa_dict[variety].get("nf_max", 10.0)
            
            osnr_i = p_in_current - nf - const_ase
            osnri_inv_sum += 10**(-osnr_i/10)
            
            p_in_current += gain # P_out del amplificador
            
            # Si es el primer booster, seteamos P_tx para el NLI
            P_tx_w = 10**(p_in_current/10) * 1e-3
            
        elif t == "Fiber":
            length = node.get("length", node.get("params", {}).get("length", 0))
            loss_coef = node.get("loss_coef", node.get("params", {}).get("loss_coef", 0.2))
            alpha_lin = (loss_coef * math.log(10)) / 10
            
            if length > 0 and alpha_lin > 0:
                L_eff = (1 - math.exp(-alpha_lin * length)) / alpha_lin
                L_effs.append(L_eff)
                N_s += 1
                total_length += length
                
            loss = (length * loss_coef) + 0.5 # Sumar 0.5 dB extra por conectores (GNPy: 0.25 in, 0.25 out)
            p_in_current -= loss
            
        elif t == "Roadm":
            p_in_current = target_pch_out
            
    if N_s == 0:
        print("  Ruta sin spans de fibra válidos.")
        return
        
    # Calculos finales
    osnr_ase_db = -10 * math.log10(osnri_inv_sum) if osnri_inv_sum > 0 else float('inf')
    
    L_eff_avg = sum(L_effs) / len(L_effs)
    
    # NLI math
    try:
        argument_log = math.pi**2 * beta2 * L_eff_avg * (N_ch**2) * (baud_rate**2)
        log_term = math.log(abs(argument_log))
        denominator = math.pi * beta2 * (baud_rate**3)
        front_term = ((2/3)**3) * N_s * (gamma_1_W_km**2) * L_eff_avg * (P_tx_w**2)
        inv_gsnr_nli = front_term * (log_term / denominator) * B_ref
        gsnr_nli_db = -10 * math.log10(inv_gsnr_nli)
    except Exception as e:
        print(f"  Error calculando NLI: {e}")
        gsnr_nli_db = float('inf')
        inv_gsnr_nli = 0
        
    inv_gsnr_red = osnri_inv_sum + inv_gsnr_nli
    gsnr_red_db = -10 * math.log10(inv_gsnr_red) if inv_gsnr_red > 0 else float('inf')
    
    inv_tx = 10**(-tx_osnr/10)
    inv_gsnr_total = inv_tx + inv_gsnr_red
    gsnr_total_db = -10 * math.log10(inv_gsnr_total) if inv_gsnr_total > 0 else float('inf')
    
    print(f"  Resultados:")
    print(f"    OSNR ASE: {osnr_ase_db:.2f} dB")
    print(f"    GSNR NLI: {gsnr_nli_db:.2f} dB")
    print(f"    GSNR Total (inc. Tx): {gsnr_total_db:.2f} dB")
    print(f"    Umbral (OSNR_req + Margen): {osnr_req + sys_margins:.2f} dB")
    
    if gsnr_total_db >= (osnr_req + sys_margins):
        print("    -> FACTIBLE ✓")
        factible = "SI"
    else:
        print("    -> NO FACTIBLE ✗")
        factible = "NO"
        
    if gsnr_total_db >= osnr_req:
        factible_sin_margen = "SI"
    else:
        factible_sin_margen = "NO"

    if gsnr_total_db >= (osnr_req - 2.5):
        factible_umbral_menos_2_5 = "SI"
    else:
        factible_umbral_menos_2_5 = "NO"
        
    return {
        "Distancia_km": round(total_length, 2),
        "OSNR_ASE_dB": round(osnr_ase_db, 2),
        "GSNR_NLI_dB": round(gsnr_nli_db, 2),
        "GSNR_Total_dB": round(gsnr_total_db, 2),
        "Factible": factible,
        "Umbral_OSNR_dB": round(osnr_req, 2),
        "Factible_Sin_Margen": factible_sin_margen,
        "Factible_Umbral_Menos_2.5": factible_umbral_menos_2_5
    }

def main():
    if not os.path.exists(DEMANDAS_FILE):
        print(f"ERROR: No se encontró el archivo {DEMANDAS_FILE}")
        return

    print("--- Procesando Demandas ---")
    
    with open(DEMANDAS_FILE, 'r', encoding='utf-8') as f, \
         open(RESULTADOS_FILE, 'w', encoding='utf-8', newline='') as out_csv:
        
        reader = csv.DictReader(f)
        fieldnames = ["Region", "Origen", "Destino", "Cantidad de Enlaces", "Velocidad [Gbps]", "Ruta", "Distancia_km", "GSNR_Total_dB", "Umbral_OSNR_dB", "Factible"]
        writer = csv.DictWriter(out_csv, fieldnames=fieldnames)
        writer.writeheader()
        
        count = 0
        total_rutas = 0
        exitosas = 0
        for row in reader:
            total_rutas += 1
            ruta_str = row.get("Path_Sequence", row.get("Ruta", ""))
            if ruta_str:
                # Limpiar la ruta de dobles espacios y espacios al principio/final
                ruta_limpia = " ".join(ruta_str.split())
                if '->' in ruta_limpia:
                    ciudades = [c.strip() for c in ruta_limpia.split('->')]
                else:
                    ciudades = [c.strip() for c in ruta_limpia.split('-')]
                
                # Desactivamos el print interno de calcular_ruta para no saturar
                import sys
                original_stdout = sys.stdout
                velocidad = row.get("Velocidad [Gbps]", "400")
                sys.stdout = open(os.devnull, 'w')
                resultado = calcular_ruta(ciudades, velocidad)
                sys.stdout = original_stdout
                
                # Actualizar la fila con los resultados si la ruta fue exitosa
                if resultado:
                    row.update(resultado)
                    exitosas += 1
                else:
                    row.update({
                        "Distancia_km": "ERROR",
                        "OSNR_ASE_dB": "ERROR",
                        "GSNR_NLI_dB": "ERROR",
                        "GSNR_Total_dB": "ERROR",
                        "Factible": "ERROR",
                        "Umbral_OSNR_dB": "ERROR",
                        "Factible_Sin_Margen": "ERROR",
                        "Factible_Umbral_Menos_2.5": "ERROR"
                    })
                
                output_row = {field: row.get(field, "") for field in fieldnames}
                writer.writerow(output_row)
                count += 1
                
        print(f"\n[INFO] Se procesaron {total_rutas} rutas totales. {exitosas} pudieron ser calculadas exitosamente. Revisá el archivo {RESULTADOS_FILE}")

if __name__ == "__main__":
    main()
