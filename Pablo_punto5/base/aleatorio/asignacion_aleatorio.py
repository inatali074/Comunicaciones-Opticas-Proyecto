import pandas as pd
import re
import random
import time

# Fijamos una semilla por reproducibilidad (para que si lo corrés varias veces te dé igual)
random.seed(42)

# =============================================================================
# DICCIONARIO DE CORRECCIÓN ORTOGRÁFICA (ARSAT CSV -> Estándar de Red)
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
    """Desglosa la columna Ruta en una secuencia orientada de enlaces nodo a nodo"""
    ciudades = [c.strip() for c in re.split(r'\s*-\s*|\s*→\s*', ruta_str) if c.strip()]
    nodos_roadm = [normalizar_ciudad(ciudad) for ciudad in ciudades]

    pares = []
    for i in range(len(nodos_roadm) - 1):
        pares.append((nodos_roadm[i], nodos_roadm[i+1]))
    return pares


# =============================================================================
# CLASE DE LA RED CON RESERVA ACUMULATIVA (MÉTODO ALEATORIO)
# =============================================================================
class RedFlexiGridAleatoria:
    def __init__(self):
        """Inicializa la estructura del espectro indexada de forma única por enlace"""
        self.espectro = {}

    def garantizar_enlace(self, par_enlace):
        """Si el enlace físico (Origen, Destino) no existe en el mapa, lo crea vacío"""
        if par_enlace not in self.espectro:
            # 304 slots vacíos representados por un string vacío ""
            self.espectro[par_enlace] = [""] * 304

    def asignar_random(self, id_demanda, lista_enlaces, slots_necesarios):
        """
        Busca TODOS los slots iniciales donde la demanda quepa de forma continua y alineada.
        Luego elige uno al azar de entre los válidos y realiza el relleno acumulativo.
        """
        # Primero garantizamos que todas las celdas de la ruta existan en nuestra matriz
        for enlace in lista_enlaces:
            self.garantizar_enlace(enlace)

        # Lista para almacenar todos los índices de slots iniciales que resulten viables
        opciones_validas = []

        # Escaneo completo del espectro para encontrar candidatos
        for start_slot in range(304 - slots_necesarios + 1):
            libre_en_toda_la_ruta = True

            # Verificar si la ventana de slots está libre en todos los tramos de la traza
            for enlace in lista_enlaces:
                bloque = self.espectro[enlace][start_slot : start_slot + slots_necesarios]
                if any(slot_celda != "" for slot_celda in bloque):
                    libre_en_toda_la_ruta = False
                    break

            if libre_en_toda_la_ruta:
                opciones_validas.append(start_slot)

        # Si encontramos al menos una opción espectral viable, elegimos una al azar
        if opciones_validas:
            slot_elegido = random.choice(opciones_validas)

            # Escribir la etiqueta en las celdas comunes de la matriz unificada
            for enlace in lista_enlaces:
                for k in range(slot_elegido, slot_elegido + slots_necesarios):
                    self.espectro[enlace][k] = id_demanda
            return True

        return False # Bloqueo espectral por falta de recursos alineados

    def exportar_matriz_unica_csv(self, nombre_archivo):
        """Exporta la grilla unificada sin repetir filas de enlaces físicos"""
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
        print(f" Matriz única acumulativa (Random) exportada: {nombre_archivo}")


# =============================================================================
# FLUJO DE EJECUCIÓN PRINCIPAL
# =============================================================================
if __name__ == "__main__":
    import os
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    print("Cargando matriz de tráfico base de ARSAT...")
    csv_path = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..', 'Demanda_Base - Tráfico base.csv'))
    df_demandas = pd.read_csv(csv_path)

    # Instanciamos nuestra red elástica acumulativa vacía
    red_nacional_random = RedFlexiGridAleatoria()

    print("Procesando demandas y rellenando la matriz mediante el método Aleatorio...")
    start_time = time.time()

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

        # Dimensionamiento de slots según criterio elástico (roll-off 0.11)
        slots_necesarios = 4 if velocidad in [100, 200] else 6

        # Asignar cada instancia de la demanda por separado
        for i in range(1, cantidad + 1):
            id_demanda = f"{origen_norm}-{destino_norm}_{velocidad}G_{i}"
            total_lightpaths += 1

            exito = red_nacional_random.asignar_random(id_demanda, enlaces_de_la_ruta, slots_necesarios)

            if exito:
                demandas_exitosas += 1
            else:
                demandas_bloqueadas += 1

    execution_time = time.time() - start_time
    prob_bloqueo = (demandas_bloqueadas / total_lightpaths) * 100

    print("\n=== REPORTE MATRIZ UNIFICADA: MÉTODO ALEATORIO ===")
    print(f"Tiempo de ejecución del algoritmo: {execution_time:.4f} segundos")
    print(f"Filas CSV (demandas únicas): {len(df_demandas)}")
    print(f"Total Lightpaths a asignar (expandido por Cantidad de Enlaces): {total_lightpaths}")
    print(f"Asignadas con Éxito: {demandas_exitosas}")
    print(f"Bloqueadas: {demandas_bloqueadas}")
    print(f"Probabilidad de Bloqueo de la Red: {prob_bloqueo:.2f}%")

    # Exportar el reporte consolidado final exigido
    output_path = os.path.join(SCRIPT_DIR, 'ocupacion_base_random.csv')
    red_nacional_random.exportar_matriz_unica_csv(output_path)

