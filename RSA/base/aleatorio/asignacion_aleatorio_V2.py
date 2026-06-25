import pandas as pd
import re
import json
import os
import random
import time

# Fijamos la semilla para la reproducibilidad
random.seed(42)

class RedFlexiGridAleatoria:
    def __init__(self):
        """
        Inicializa la grilla espectral indexada de forma única por enlace.
        """
        self.espectro = {}

    def garantizar_enlace(self, par_enlace):
        """
        Crea el tramo en la matriz si no existe, así como su reverso, con 304 slots libres ("").
        """
        if par_enlace not in self.espectro:
            self.espectro[par_enlace] = [""] * 304
        reverso = (par_enlace[1], par_enlace[0])
        if reverso not in self.espectro:
            self.espectro[reverso] = [""] * 304

    def asignar_random(self, id_demanda, lista_enlaces, slots_necesarios):
        """
        Busca todos los slots iniciales libres y alineados en todos los enlaces de la ruta (ida y vuelta).
        Si hay opciones válidas, elige una de forma aleatoria y reserva en ambos sentidos.
        """
        for enlace in lista_enlaces:
            self.garantizar_enlace(enlace)

        opciones_validas = []

        # Buscar todos los slots de inicio viables
        for start_slot in range(304 - slots_necesarios + 1):
            libre_en_toda_la_ruta = True

            for enlace in lista_enlaces:
                reverso = (enlace[1], enlace[0])
                bloque_ida = self.espectro[enlace][start_slot : start_slot + slots_necesarios]
                bloque_vuelta = self.espectro[reverso][start_slot : start_slot + slots_necesarios]
                if any(slot != "" for slot in bloque_ida) or any(slot != "" for slot in bloque_vuelta):
                    libre_en_toda_la_ruta = False
                    break

            if libre_en_toda_la_ruta:
                opciones_validas.append(start_slot)

        # Si hay opciones, seleccionamos una al azar
        if opciones_validas:
            slot_elegido = random.choice(opciones_validas)
            for enlace in lista_enlaces:
                reverso = (enlace[1], enlace[0])
                for k in range(slot_elegido, slot_elegido + slots_necesarios):
                    self.espectro[enlace][k] = id_demanda
                    self.espectro[reverso][k] = id_demanda
            return True

        return False

    def exportar_csv_final(self, nombre_archivo):
        """
        Exporta la matriz consolidada respetando el formato de 306 columnas.
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
        print(f" Matriz única acumulativa (Random V2) exportada: {nombre_archivo}")


def bfs_shortest_path(start, end, adj):
    """
    Realiza una búsqueda por anchura (BFS) en el grafo físico de elementos.
    """
    if start == end:
        return [start]
    queue = [[start]]
    visited = {start}
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


def resolve_roadm(ciudad_str, elements, prev_node=None, next_ciudad_str=None, adj=None):
    """
    Resuelve el nombre de una ciudad a su correspondiente UID de ROADM en la topología.
    Usa coincidencia de texto flexible y la distancia BFS para desambiguar.
    """
    ciudad_clean = ciudad_str.strip().lower()
    
    custom_normalization = {
        "tucuman": "san miguel de tucuman",
        "san miguel de tucumán": "san miguel de tucuman",
        "media agua": "villa media agua",
        "tulumaya": "villa tulumaya",
        "jujuy": "san salvador de jujuy",
        "saenz peña": "presidencia roque saenz peña",
        "san pedro": "san pedro",
        "san martin": "san martin",
        "juan page": "cap juan page",
        "gral. alvear": "gral. alvear",
        "general alvear": "gral. alvear",
        "san nicolas": "san nicolas de los arroyos",
        "paso de los libres": "paso de los libres",
        "pehuajó": "pehuajo"
    }
    
    mapped = custom_normalization.get(ciudad_clean, ciudad_clean)
    
    candidates = []
    for k in elements:
        if k.startswith("roadm "):
            node_name = k[len("roadm "):].lower()
            if mapped in node_name:
                candidates.append(k)
                
    if not candidates:
        words = mapped.split()
        for k in elements:
            if k.startswith("roadm "):
                node_name = k[len("roadm "):].lower()
                if any(w in node_name for w in words):
                    candidates.append(k)
                    
    if not candidates:
        return None
        
    if len(candidates) == 1:
        return candidates[0]
        
    # Resolver homónimos mediante proximidad en el grafo (BFS)
    if prev_node and adj:
        best_cand = None
        best_dist = float('inf')
        for cand in candidates:
            p = bfs_shortest_path(prev_node, cand, adj)
            if p:
                dist = len(p)
                if dist < best_dist:
                    best_dist = dist
                    best_cand = cand
        if best_cand:
            return best_cand
            
    if next_ciudad_str and adj:
        next_mapped = custom_normalization.get(next_ciudad_str.strip().lower(), next_ciudad_str.strip().lower())
        next_candidates = []
        for k in elements:
            if k.startswith("roadm "):
                node_name = k[len("roadm "):].lower()
                if next_mapped in node_name:
                    next_candidates.append(k)
                    
        if next_candidates:
            best_cand = None
            best_dist = float('inf')
            for cand in candidates:
                for n_cand in next_candidates:
                    p = bfs_shortest_path(cand, n_cand, adj)
                    if p:
                        dist = len(p)
                        if dist < best_dist:
                            best_dist = dist
                            best_cand = cand
            if best_cand:
                return best_cand
                
    candidates.sort(key=len)
    return candidates[0]


def find_file(filename, search_dirs):
    """
    Busca un archivo en una lista de directorios.
    """
    for d in search_dirs:
        path = os.path.join(d, filename)
        if os.path.exists(path):
            return os.path.abspath(path)
    return None


if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Directorios de búsqueda de archivos (para máxima portabilidad)
    search_dirs = [
        '.',
        SCRIPT_DIR,
        os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..')),
        os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..', 'Consigna')),
        os.path.abspath(os.path.join(SCRIPT_DIR, 'Consigna'))
    ]
    
    network_path = find_file('network_mashe.json', search_dirs)
    demanda_path = find_file('Demanda_Base - Tráfico base.csv', search_dirs)
    
    if not network_path or not demanda_path:
        print("ERROR: No se pudieron localizar todos los archivos necesarios.")
        print(f"network_mashe.json encontrado en: {network_path}")
        print(f"Demanda_Base - Tráfico base.csv encontrado en: {demanda_path}")
        exit(1)
        
    print(f"Cargando topología de red: {network_path}")
    with open(network_path, 'r', encoding='utf-8') as f:
        network_data = json.load(f)
        
    print(f"Cargando demandas base: {demanda_path}")
    df_demandas = pd.read_csv(demanda_path)
    
    elements = {e["uid"]: e for e in network_data.get("elements", [])}
    connections = network_data.get("connections", [])
    
    adj = {uid: [] for uid in elements}
    for conn in connections:
        u = conn["from_node"]
        v = conn["to_node"]
        if u in adj:
            adj[u].append(v)
            
    mi_red_nacional = RedFlexiGridAleatoria()
    
    print("\nEjecutando asignación incremental Aleatoria con ruteo y resolución de nombres precisa...")
    start_time = time.time()
    
    demandas_exitosas = 0
    demandas_bloqueadas = 0
    demandas_ignoradas_ruteo = 0
    total_lightpaths = 0
    
    problemas_ruteacion = []
    
    for index, fila in df_demandas.iterrows():
        csv_row_num = index + 2
        ruta_str = fila['Ruta']
        velocidad = fila['Velocidad [Gbps]']
        cantidad = int(fila['Cantidad de Enlaces'])
        
        # Desglosar nombres de ciudades del CSV
        ciudades_crudas = [c.strip() for c in re.split(r'\s*-\s*|\s*→\s*', ruta_str) if c.strip()]
        
        # Eliminar "La Paz" si no es ROADM (es decir, el La Paz de Cuyo/Mendoza)
        ciudades = []
        for i, ciudad in enumerate(ciudades_crudas):
            if ciudad.lower() == "la paz":
                es_la_paz_cuyo = False
                if i > 0 and ciudades_crudas[i-1].lower() in ["san luis", "santa rosa", "mendoza"]:
                    es_la_paz_cuyo = True
                if i + 1 < len(ciudades_crudas) and ciudades_crudas[i+1].lower() in ["san luis", "santa rosa", "mendoza"]:
                    es_la_paz_cuyo = True
                if es_la_paz_cuyo:
                    continue
            ciudades.append(ciudad)
            
        nodos_ruta_resueltos = []
        skip_demanda = False
        
        for i, ciudad in enumerate(ciudades):
            prev_node = nodos_ruta_resueltos[-1] if nodos_ruta_resueltos else None
            next_ciudad = ciudades[i+1] if i + 1 < len(ciudades) else None
            
            resolved = resolve_roadm(ciudad, elements, prev_node, next_ciudad, adj)
            if not resolved:
                print(f"  [ERROR RESOLUCIÓN] Fila CSV #{csv_row_num}: No se encontró ROADM en la topología para la ciudad '{ciudad}'")
                problemas_ruteacion.append({
                    "fila": csv_row_num,
                    "error_type": "Resolución de ciudad",
                    "origen": fila['Origen'],
                    "destino": fila['Destino'],
                    "tramo_involucrado": ciudad
                })
                skip_demanda = True
                break
            nodos_ruta_resueltos.append(resolved)
            
        if skip_demanda:
            demandas_ignoradas_ruteo += cantidad
            continue
            
        ruta_roadms_expandida = []
        error_conexion = False
        
        for i in range(len(nodos_ruta_resueltos) - 1):
            start_node = nodos_ruta_resueltos[i]
            end_node = nodos_ruta_resueltos[i+1]
            
            sub_path = bfs_shortest_path(start_node, end_node, adj)
            if not sub_path:
                print(f"  [ERROR RUTEACIÓN] Fila CSV #{csv_row_num}: Sin conexión física en la red entre '{ciudades[i]}' ({start_node}) y '{ciudades[i+1]}' ({end_node})")
                problemas_ruteacion.append({
                    "fila": csv_row_num,
                    "error_type": "Falta de camino físico",
                    "origen": fila['Origen'],
                    "destino": fila['Destino'],
                    "tramo_involucrado": f"{ciudades[i]} ({start_node}) -> {ciudades[i+1]} ({end_node})"
                })
                error_conexion = True
                break
                
            sub_roadms = [node for node in sub_path if node.startswith("roadm ")]
            
            if i == 0:
                ruta_roadms_expandida.extend(sub_roadms)
            else:
                ruta_roadms_expandida.extend(sub_roadms[1:])
                
        if error_conexion:
            demandas_ignoradas_ruteo += cantidad
            continue
            
        enlaces_de_la_ruta = []
        for i in range(len(ruta_roadms_expandida) - 1):
            enlaces_de_la_ruta.append((ruta_roadms_expandida[i], ruta_roadms_expandida[i+1]))
            
        slots_necesarios = 4 if velocidad in [100, 200] else 6
        
        resolved_origen = nodos_ruta_resueltos[0]
        resolved_destino = nodos_ruta_resueltos[-1]
        
        for i in range(1, cantidad + 1):
            id_demanda = f"{resolved_origen}-{resolved_destino}_{velocidad}G_{i}"
            total_lightpaths += 1
            
            exito = mi_red_nacional.asignar_random(id_demanda, enlaces_de_la_ruta, slots_necesarios)
            
            if exito:
                demandas_exitosas += 1
            else:
                demandas_bloqueadas += 1
                
    execution_time = time.time() - start_time
    
    print("\n=== REPORTE MATRIZ UNIFICADA: MÉTODO ALEATORIO V2 ===")
    print(f"Tiempo de ejecución: {execution_time:.4f} segundos")
    print(f"Filas CSV (demandas únicas): {len(df_demandas)}")
    print(f"Total Lightpaths procesados: {total_lightpaths}")
    print(f"Asignadas con Éxito: {demandas_exitosas}")
    print(f"Bloqueadas: {demandas_bloqueadas}")
    print(f"Ignoradas por Ruteo/Resolución: {demandas_ignoradas_ruteo}")
    
    if total_lightpaths > 0:
        prob_bloqueo = (demandas_bloqueadas / total_lightpaths) * 100
        print(f"Probabilidad de Bloqueo de la Red: {prob_bloqueo:.2f}%")
    else:
        print("Probabilidad de Bloqueo de la Red: 0.00%")
        
    if problemas_ruteacion:
        print(f"\n[ALERT] Se detectaron {len(problemas_ruteacion)} discrepancias de conectividad en el CSV:")
        for prob_item in problemas_ruteacion:
            print(f"  - Fila CSV #{prob_item['fila']}: Demanda '{prob_item['origen']} -> {prob_item['destino']}'. Error: {prob_item['error_type']} en tramo '{prob_item['tramo_involucrado']}'")
            
    output_path = os.path.join(SCRIPT_DIR, 'ocupacion_base_random_V2.csv')
    mi_red_nacional.exportar_csv_final(output_path)
