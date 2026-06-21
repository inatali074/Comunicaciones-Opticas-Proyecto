import pandas as pd
import re

class RedFlexiGridConsolidada:
    def __init__(self):
        """
        Inicializa la matriz espectral de la red nacional de forma indexada y única.
        """
        self.espectro = {}

    def garantizar_enlace(self, par_enlace):
        """
        Si el tramo orientado (Nodo_Origen, Nodo_Destino) no existe en la matriz,
        lo crea con sus 304 slots completamente libres ("").
        """
        if par_enlace not in self.espectro:
            self.espectro[par_enlace] = [""] * 304

    def asignar_first_fit(self, id_demanda, lista_enlaces, slots_necesarios):
        """
        Busca el PRIMER slot inicial libre alineado en todos los enlaces de la ruta.
        Si está libre, escribe la etiqueta real de la demanda en la matriz global.
        """
        # Asegurar que todos los tramos de la traza existan en la matriz
        for enlace in lista_enlaces:
            self.garantizar_enlace(enlace)

        # Recorremos los 304 slots de izquierda a derecha
        for start_slot in range(304 - slots_necesarios + 1):
            libre_en_toda_la_ruta = True

            # PASO 1: Verificar si la ventana está 100% libre (vacía "") en toda la traza física
            for enlace in lista_enlaces:
                bloque = self.espectro[enlace][start_slot : start_slot + slots_necesarios]
                if any(slot_celda != "" for slot_celda in bloque):
                    libre_en_toda_la_ruta = False
                    break

            # PASO 2: Si está libre, grabamos la etiqueta de esta demanda en las celdas comunes
            if libre_en_toda_la_ruta:
                for enlace in lista_enlaces:
                    for k in range(start_slot, start_slot + slots_necesarios):
                        self.espectro[enlace][k] = id_demanda
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


# =============================================================================
# DICCIONARIO DE NORMALIZACIÓN ORTOGRÁFICA
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
    """Convierte la traza de texto del CSV en pares ordenados secuenciales"""
    ciudades = [c.strip() for c in re.split(r'\s*-\s*|\s*→\s*', ruta_str) if c.strip()]
    nodos_roadm = [normalizar_ciudad(ciudad) for ciudad in ciudades]

    pares = []
    for i in range(len(nodos_roadm) - 1):
        pares.append((nodos_roadm[i], nodos_roadm[i+1]))
    return pares


# =============================================================================
# PROGRAMA PRINCIPAL DE SIMULACIÓN CORREGIDO
# =============================================================================
if __name__ == "__main__":
    import os
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    print("Cargando matriz de tráfico base de ARSAT...")
    csv_path = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..', 'Demanda_Base - Tráfico base.csv'))
    df_demandas = pd.read_csv(csv_path)

    # Instanciar el objeto de red global único
    mi_red_nacional = RedFlexiGridConsolidada()

    print("Ejecutando asignación incremental y empaquetamiento First-Fit...")
    demandas_exitosas = 0
    demandas_bloqueadas = 0

    total_lightpaths = 0

    for index, fila in df_demandas.iterrows():
        origen_norm = normalizar_ciudad(fila['Origen'])
        destino_norm = normalizar_ciudad(fila['Destino'])
        velocidad = fila['Velocidad [Gbps]']
        cantidad = int(fila['Cantidad de Enlaces'])

        # Desglosar los saltos orientados de la columna Ruta
        enlaces_de_la_ruta = extraer_pares_nodo_a_nodo(fila['Ruta'])

        # Tamaño del bloque espectral (roll-off de 0.11 para el Grupo 2)
        slots_necesarios = 4 if velocidad in [100, 200] else 6

        # Asignar cada instancia de la demanda por separado
        for i in range(1, cantidad + 1):
            id_demanda = f"{origen_norm}-{destino_norm}_{velocidad}G_{i}"
            total_lightpaths += 1

            exito = mi_red_nacional.asignar_first_fit(id_demanda, enlaces_de_la_ruta, slots_necesarios)

            if exito:
                demandas_exitosas += 1
            else:
                print(f"  [BLOQUEO ESPECTRAL] Sin espacio continuo para: {id_demanda}")
                demandas_bloqueadas += 1

    print("\n=== REPORTE REVISADO CON MÁXIMA PRECISIÓN ===")
    print(f"Filas CSV (demandas únicas): {len(df_demandas)}")
    print(f"Total Lightpaths a asignar (expandido por Cantidad de Enlaces): {total_lightpaths}")
    print(f"Asignadas con Éxito: {demandas_exitosas}")
    print(f"Bloqueadas: {demandas_bloqueadas}")
    prob_bloqueo = (demandas_bloqueadas / total_lightpaths) * 100
    print(f"Probabilidad de Bloqueo Final: {prob_bloqueo:.2f}%")

    # Guardar el CSV único consolidado
    output_path = os.path.join(SCRIPT_DIR, 'ocupacion_base_firstfit.csv')
    mi_red_nacional.exportar_csv_final(output_path)

