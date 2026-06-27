import pandas as pd
import re
import json
import os
import time

class RedFlexiGridConsolidada:
    def __init__(self):
        """
        Inicializa la matriz espectral de la red nacional de forma indexada y única.
        """
        self.espectro = {}
        # Diccionarios para rastrear solicitudes y bloqueos por enlace (para P_bloqueo por enlace)
        self.link_requests = {}
        self.link_blocks = {}

    def garantizar_enlace(self, par_enlace):
        """
        Si el tramo orientado (Nodo_Origen, Nodo_Destino) o su reverso no existen en la matriz,
        los crea con sus 304 slots completamente libres ("").
        """
        if par_enlace not in self.espectro:
            self.espectro[par_enlace] = [""] * 304
        reverso = (par_enlace[1], par_enlace[0])
        if reverso not in self.espectro:
            self.espectro[reverso] = [""] * 304

    def registrar_intento(self, lista_enlaces, fue_bloqueado):
        """
        Registra un intento de asignación sobre una ruta (lista de enlaces).
        Si fue bloqueado, incrementa la cuenta de bloqueos en esos enlaces.
        """
        for enlace in lista_enlaces:
            self.garantizar_enlace(enlace)
            reverso = (enlace[1], enlace[0])
            
            # Registrar en el sentido directo
            self.link_requests[enlace] = self.link_requests.get(enlace, 0) + 1
            if fue_bloqueado:
                self.link_blocks[enlace] = self.link_blocks.get(enlace, 0) + 1
                
            # Registrar en el sentido reverso (ya que la asignación es bidireccional)
            self.link_requests[reverso] = self.link_requests.get(reverso, 0) + 1
            if fue_bloqueado:
                self.link_blocks[reverso] = self.link_blocks.get(reverso, 0) + 1

    def asignar_first_fit(self, id_demanda, lista_enlaces, slots_necesarios):
        """
        Busca el PRIMER slot inicial libre alineado en todos los enlaces de la ruta (ida y vuelta).
        Si está libre, escribe la etiqueta real de la demanda en ambos sentidos de la matriz global.
        """
        # Asegurar que todos los tramos de la traza (y sus reversos) existan en la matriz
        for enlace in lista_enlaces:
            self.garantizar_enlace(enlace)

        # Recorremos los 304 slots de izquierda a derecha
        for start_slot in range(304 - slots_necesarios + 1):
            libre_en_toda_la_ruta = True

            # PASO 1: Verificar si la ventana está 100% libre (vacía "") en toda la traza física (ida y vuelta)
            for enlace in lista_enlaces:
                reverso = (enlace[1], enlace[0])
                bloque_ida = self.espectro[enlace][start_slot : start_slot + slots_necesarios]
                bloque_vuelta = self.espectro[reverso][start_slot : start_slot + slots_necesarios]
                if any(slot != "" for slot in bloque_ida) or any(slot != "" for slot in bloque_vuelta):
                    libre_en_toda_la_ruta = False
                    break

            # PASO 2: Si está libre, grabamos la etiqueta de esta demanda en las celdas comunes (ida y vuelta)
            if libre_en_toda_la_ruta:
                for enlace in lista_enlaces:
                    reverso = (enlace[1], enlace[0])
                    for k in range(start_slot, start_slot + slots_necesarios):
                        self.espectro[enlace][k] = id_demanda
                        self.espectro[reverso][k] = id_demanda
                return True # Asignación exitosa

        return False # Bloqueo por espectro lleno

    def exportar_csv_final(self, nombre_archivo):
        """
        Exporta la matriz consolidada respetando el formato de 306 columnas.
        Cada enlace físico orientado aparece una única vez.
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
        print(f" Matriz única corregida exportada exitosamente: {nombre_archivo}")

    def calcular_metricas_calidad(self):
        """
        Calcula las métricas de calidad de la red enlace por enlace y sus promedios:
        - Fragmentación de espectro
        - Contigüidad de espectro
        - Ocupación de slots
        - Probabilidad de bloqueo
        """
        metricas_enlaces = {}
        
        for enlace, slots in self.espectro.items():
            total_slots = len(slots)  # 304
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
    Usa coincidencia de texto flexible y heurística de caminos en el grafo para
    resolver ambigüedades (como Santa Rosa (LP) vs Santa Rosa (Mza)).
    """
    ciudad_clean = ciudad_str.strip().lower()
    
    # Normalizaciones ortográficas manuales para corregir discrepancias del CSV
    custom_normalization = {
        "tucuman": "san miguel de tucuman",
        "san miguel de tucumán": "san miguel de tucuman",
        "media agua": "villa media agua",
        "tulumaya": "villa tulumaya",
        "jujuy": "san salvador de jujuy",
        "saenz peña": "presidencia roque saenz peña",
        "san pedro": "san pedro",  # Resuelto dinámicamente según vecindad
        "san martin": "san martin",  # Resuelto dinámicamente según vecindad
        "juan page": "cap juan page",
        "gral. alvear": "gral. alvear",
        "general alvear": "gral. alvear",
        "san nicolas": "san nicolas de los arroyos",
        "paso de los libres": "paso de los libres",
        "pehuajó": "pehuajo"
    }
    
    mapped = custom_normalization.get(ciudad_clean, ciudad_clean)
    
    # 1. Buscar coincidencia en ROADMs
    candidates = []
    for k in elements:
        if k.startswith("roadm "):
            node_name = k[len("roadm "):].lower()
            if mapped in node_name:
                candidates.append(k)
                
    # Fallback si no se encontró con coincidencia exacta de subcadena
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
        
    # 2. Si hay múltiples candidatos, resolver por proximidad en el grafo (BFS)
    # A. Probar proximidad con el nodo resuelto inmediatamente anterior
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
            
    # B. Si no hay nodo anterior (es el origen), probar proximidad con el candidato del nodo siguiente
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
                
    # Fallback final: Devolver el candidato con nombre más corto/específico
    candidates.sort(key=len)
    return candidates[0]


def find_file(filename, search_dirs):
    """
    Busca un archivo en una lista de directorios permitidos.
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
        os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..', '..')),
        os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..', 'Consigna')),
        os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..', '..', 'Consigna')),
        os.path.abspath(os.path.join(SCRIPT_DIR, 'Consigna'))
    ]
    
    # Localizar archivos
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
    
    # Parsear elementos y conexiones para crear el grafo de adjacencia
    elements = {e["uid"]: e for e in network_data.get("elements", [])}
    connections = network_data.get("connections", [])
    
    adj = {uid: [] for uid in elements}
    for conn in connections:
        u = conn["from_node"]
        v = conn["to_node"]
        if u in adj:
            adj[u].append(v)
            
    # Instanciar el objeto de red global único
    mi_red_nacional = RedFlexiGridConsolidada()
    
    print("\nEjecutando asignación incremental First-Fit con ruteo y resolución de nombres precisa...")
    demandas_exitosas = 0
    demandas_bloqueadas = 0
    demandas_ignoradas_ruteo = 0
    total_lightpaths = 0
    
    # Lista para registrar las demandas que no pudieron rutearse
    problemas_ruteacion = []
    
    # Lista para el diccionario de demandas
    demandas_dict_list = []
    # Lista para el mapeo de lightpaths
    mapping_list = []
    
    # Lista para registrar los tiempos de ejecución por demanda individual
    tiempos_demandas = []
    
    for index, fila in df_demandas.iterrows():
        csv_row_num = index + 2  # Pandas 0-indexed corresponde a línea 2 del CSV
        ruta_str = fila['Ruta']
        velocidad = fila['Velocidad [Gbps]']
        cantidad = int(fila['Cantidad de Enlaces'])
        
        # Generar ID corto de demanda
        id_demanda_num = f"D{index+1}"
        demandas_dict_list.append({
            "ID_Demanda": id_demanda_num,
            "Origen": fila['Origen'],
            "Destino": fila['Destino'],
            "Cantidad de Enlaces": cantidad,
            "Velocidad [Gbps]": velocidad,
            "Ruta": ruta_str
        })
        
        # --- INICIO MEDICIÓN DE TIEMPO (Ruteo) ---
        t0 = time.perf_counter()
        
        # Desglosar nombres de ciudades del CSV
        ciudades_crudas = [c.strip() for c in re.split(r'\s*-\s*|\s*→\s*', ruta_str) if c.strip()]
        
        # Eliminar "La Paz" si no es ROADM (es decir, el La Paz de Cuyo/Mendoza)
        ciudades = []
        for i, ciudad in enumerate(ciudades_crudas):
            if ciudad.lower() == "la paz":
                # Si está rodeado de San Luis, Santa Rosa o Mendoza, es el La Paz de Cuyo
                es_la_paz_cuyo = False
                if i > 0 and ciudades_crudas[i-1].lower() in ["san luis", "santa rosa", "mendoza"]:
                    es_la_paz_cuyo = True
                if i + 1 < len(ciudades_crudas) and ciudades_crudas[i+1].lower() in ["san luis", "santa rosa", "mendoza"]:
                    es_la_paz_cuyo = True
                if es_la_paz_cuyo:
                    continue  # Omitir La Paz (Mza) ya que no es un ROADM
            ciudades.append(ciudad)
        
        # 1. Resolver cada ciudad del CSV a su ROADM correspondiente en el grafo
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
            
        # 2. Expandir la ruta secuencialmente usando BFS para incluir ROADMs intermedios no listados
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
            
            # Filtrar solo elementos ROADM del subcamino
            sub_roadms = [node for node in sub_path if node.startswith("roadm ")]
            
            if i == 0:
                ruta_roadms_expandida.extend(sub_roadms)
            else:
                ruta_roadms_expandida.extend(sub_roadms[1:])  # Evitar duplicar el nodo de unión
                
        if error_conexion:
            demandas_ignoradas_ruteo += cantidad
            continue
            
        # Generar pares ordenados de enlaces físicos reales
        enlaces_de_la_ruta = []
        for i in range(len(ruta_roadms_expandida) - 1):
            enlaces_de_la_ruta.append((ruta_roadms_expandida[i], ruta_roadms_expandida[i+1]))
            
        # Tamaño del bloque espectral
        slots_necesarios = 4 if velocidad in [100, 200] else 6
        
        # Tiempo tomado para rutear esta fila
        t_route_elapsed = time.perf_counter() - t0
        
        # 3. Asignar cada instancia de la demanda
        resolved_origen = nodos_ruta_resueltos[0]
        resolved_destino = nodos_ruta_resueltos[-1]
        for i in range(1, cantidad + 1):
            id_demanda_long = f"{resolved_origen}-{resolved_destino}_{velocidad}G_{i}"
            total_lightpaths += 1
            
            # --- INICIO MEDICIÓN TIEMPO ASIGNACIÓN ---
            t_alloc_0 = time.perf_counter()
            
            exito = mi_red_nacional.asignar_first_fit(id_demanda_long, enlaces_de_la_ruta, slots_necesarios)
            
            t_alloc_elapsed = time.perf_counter() - t_alloc_0
            # Tiempo total de ruteo + asignación para esta demanda individual
            t_demanda_total = t_route_elapsed + t_alloc_elapsed
            tiempos_demandas.append(t_demanda_total)
            
            # Registrar el intento con su resultado
            mi_red_nacional.registrar_intento(enlaces_de_la_ruta, fue_bloqueado=not exito)
            
            if exito:
                demandas_exitosas += 1
                mapping_list.append({
                    "Nombre_Lightpath": id_demanda_long,
                    "ID_Demanda": id_demanda_num,
                    "Velocidad": f"{velocidad}G",
                    "Instancia": i
                })
            else:
                print(f"  [BLOQUEO ESPECTRAL] Sin espacio continuo para: {id_demanda_long}")
                demandas_bloqueadas += 1

    # Calcular estadísticas de red
    stats_enlaces = mi_red_nacional.calcular_metricas_calidad()
    
    # ----------------------------------------------------
    # Procesar métricas generales de calidad
    # ----------------------------------------------------
    # 1. Tiempos
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
    
    # 4. Probabilidad de bloqueo promedio por enlace
    block_prob_list = [info["prob_bloqueo_pct"] for info in stats_enlaces.values()]
    avg_link_block_prob = sum(block_prob_list) / len(block_prob_list) if block_prob_list else 0

    # 5. Transiciones ocupado-a-libre
    trans_list = [info["transiciones_occ_lib"] for info in stats_enlaces.values()]
    min_trans = min(trans_list) if trans_list else 0
    max_trans = max(trans_list) if trans_list else 0
    avg_trans = sum(trans_list) / len(trans_list) if trans_list else 0

    # Reporte por consola
    print("\n=== REPORTE REVISADO CON MÁXIMA PRECISIÓN (V3 - MÉTRICAS DE CALIDAD) ===")
    print(f"Filas CSV (demandas únicas): {len(df_demandas)}")
    print(f"Total Lightpaths procesados en la simulación: {total_lightpaths}")
    print(f"Asignadas con Éxito (First-Fit): {demandas_exitosas}")
    print(f"Bloqueadas por Falta de Espectro: {demandas_bloqueadas}")
    print(f"Ignoradas por Errores de Ruteo/Resolución: {demandas_ignoradas_ruteo}")
    
    if total_lightpaths > 0:
        prob_bloqueo_global = (demandas_bloqueadas / total_lightpaths) * 100
        print(f"Probabilidad de Bloqueo Espectral Global: {prob_bloqueo_global:.2f}%")
    else:
        prob_bloqueo_global = 0.0
        print("Probabilidad de Bloqueo Espectral Global: 0.00% (No se asignaron lightpaths)")

    print("\n--- METRICAS DE TIEMPO POR DEMANDA INDIVIDUAL ---")
    print(f"Tiempo mínimo:  {min_time*1000:.4f} ms")
    print(f"Tiempo máximo:  {max_time*1000:.4f} ms")
    print(f"Tiempo promedio: {avg_time*1000:.4f} ms")
    
    print("\n--- METRICAS DE GRIDS Y ESPECTRO DE LA RED ---")
    print(f"Ocupación promedio de slots por enlace: {avg_occ:.2f} slots ({avg_occ/304*100:.2f}%)")
    print(f"Enlace menos cargado: {min_occ} slots | Enlace más cargado: {max_occ} slots")
    print(f"Variación de la carga (Max - Min): {var_occ} slots")
    print(f"Fragmentación espectral promedio de la red: {avg_frag:.4f}")
    print(f"Contigüidad espectral promedio de la red:   {avg_contig:.4f}")
    print(f"Tamaño promedio del bloque libre máximo:    {avg_max_free_block:.2f} slots")
    print(f"Transiciones ocupado-a-libre promedio:      {avg_trans:.4f} (mín: {min_trans}, máx: {max_trans})")
    print(f"Probabilidad de bloqueo promedio por enlace: {avg_link_block_prob:.2f}%")
    
    # Reporte de problemas de ruteación para resolución manual
    if problemas_ruteacion:
        print(f"\n[ALERT] Se detectaron {len(problemas_ruteacion)} discrepancias de conectividad en el CSV:")
        for prob_item in problemas_ruteacion:
            print(f"  - Fila CSV #{prob_item['fila']}: Demanda '{prob_item['origen']} -> {prob_item['destino']}'. Error: {prob_item['error_type']} en tramo '{prob_item['tramo_involucrado']}'")
            
    # Guardar el CSV único consolidado
    output_path = os.path.join(SCRIPT_DIR, 'ocupacion_base_firstfit_V3_metricas.csv')
    mi_red_nacional.exportar_csv_final(output_path)
    
    # Guardar el diccionario de demandas
    df_dict = pd.DataFrame(demandas_dict_list)
    dict_output_path = os.path.join(SCRIPT_DIR, 'lista_demandas_firstfit_V3_metricas.csv')
    df_dict.to_csv(dict_output_path, index=False)
    print(f" Diccionario de demandas exportado exitosamente: {dict_output_path}")
    
    # Guardar el mapeo de lightpaths
    df_map = pd.DataFrame(mapping_list)
    map_output_path = os.path.join(SCRIPT_DIR, 'mapping_lightpaths_firstfit_V3_metricas.csv')
    df_map.to_csv(map_output_path, index=False)
    print(f" Mapeo de lightpaths exportado exitosamente: {map_output_path}")
    
    # Guardar un reporte de texto detallado de métricas por enlace
    reporte_txt_path = os.path.join(SCRIPT_DIR, 'reporte_base_firstfit_V3_metricas.txt')
    with open(reporte_txt_path, 'w', encoding='utf-8') as f_rep:
        f_rep.write("=" * 80 + "\n")
        f_rep.write("  REPORTE DETALLADO DE MÉTRICAS DE CALIDAD - TRÁFICO BASE (FIRST-FIT V3)\n")
        f_rep.write("=" * 80 + "\n\n")
        
        f_rep.write("--- MÉTODOLOGÍA ---\n")
        f_rep.write("Tiempos por Demanda: Medidos por cada instancia individual (incluye tiempo de ruteo BFS y tiempo de asignación First-Fit).\n")
        f_rep.write("Fragmentación de Espectro (F): F = 1 - (Max_Bloque_Libre / Slots_Libres). F = 0 indica grilla compacta; F = 1 indica totalmente fragmentado.\n")
        f_rep.write("Contigüidad del Espectro (C): C = Sum(s_i^2) / S_libres^2. C = 1 indica contigüidad perfecta (un solo bloque libre).\n")
        f_rep.write("Variación de la Carga: Diferencia entre el enlace con más slots ocupados y el enlace con menos slots ocupados.\n")
        f_rep.write("Probabilidad de Bloqueo por Enlace: Bloqueos experimentados en el enlace / Total solicitudes de paso por el enlace.\n\n")
        
        f_rep.write("--- RESUMEN GLOBAL DE LA RED ---\n")
        f_rep.write(f"Total Demandas Procesadas: {total_lightpaths}\n")
        f_rep.write(f"Exitosas:                  {demandas_exitosas}\n")
        f_rep.write(f"Bloqueadas:                {demandas_bloqueadas}\n")
        f_rep.write(f"Prob. Bloqueo Global:      {prob_bloqueo_global:.4f}%\n\n")
        
        f_rep.write("--- MÉTRIAS DE TIEMPO POR DEMANDA INDIVIDUAL ---\n")
        f_rep.write(f"Mínimo:                    {min_time*1000:.4f} ms\n")
        f_rep.write(f"Máximo:                    {max_time*1000:.4f} ms\n")
        f_rep.write(f"Promedio:                  {avg_time*1000:.4f} ms\n\n")
        
        f_rep.write("--- ESTRUCTURA DE ESPECTRO GLOBAL ---\n")
        f_rep.write(f"Ocupación Promedio:        {avg_occ:.2f} slots ({avg_occ/304*100:.2f}%)\n")
        f_rep.write(f"Carga Mínima de Enlace:    {min_occ} slots\n")
        f_rep.write(f"Carga Máxima de Enlace:    {max_occ} slots\n")
        f_rep.write(f"Variación de Carga (Max-Min): {var_occ} slots\n")
        f_rep.write(f"Fragmentación Promedio:    {avg_frag:.6f}\n")
        f_rep.write(f"Contigüidad Promedio:      {avg_contig:.6f}\n")
        f_rep.write(f"Bloque Libre Máx. Promedio: {avg_max_free_block:.2f} slots\n")
        f_rep.write(f"Transiciones Ocupado-Libre (min/max/prom): {min_trans} / {max_trans} / {avg_trans:.4f}\n")
        f_rep.write(f"Prob. Bloqueo Promedio Enlace: {avg_link_block_prob:.4f}%\n\n")
        
        f_rep.write("--- MÉTRIAS ENLACE POR ENLACE ---\n")
        f_rep.write(f"{'Enlace (Origen -> Destino)':<60} | {'Ocupados':<8} | {'Libres':<8} | {'Frag (F)':<8} | {'Contig (C)':<10} | {'Trans O->L':<10} | {'Solics':<7} | {'Bloqs':<6} | {'P_block%':<8}\n")
        f_rep.write("-" * 148 + "\n")
        
        for enlace, info in sorted(stats_enlaces.items()):
            enlace_str = f"{enlace[0].replace('roadm ', '')} -> {enlace[1].replace('roadm ', '')}"
            f_rep.write(f"{enlace_str:<60} | {info['slots_ocupados']:8d} | {info['slots_libres']:8d} | {info['fragmentacion']:8.4f} | {info['contiguidad']:10.4f} | {info['transiciones_occ_lib']:10d} | {info['solicitudes']:7d} | {info['bloqueos']:6d} | {info['prob_bloqueo_pct']:7.2f}%\n")
            
    print(f" Reporte detallado de métricas exportado exitosamente: {reporte_txt_path}")
