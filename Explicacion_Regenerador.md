# Explicación Detallada: `Regenerador.py`

El script **`Regenerador.py`** funciona como un procesador de post-simulación en la capa física. Su propósito principal es tomar los resultados donde la relación Señal a Ruido (GSNR) de extremo a extremo no fue suficiente para transportar el tráfico, y ubicar automáticamente **equipos de regeneración física O-E-O (Óptico-Eléctrico-Óptico)** para hacer que la ruta sea factible.

Todo el proceso de regeneración se basa en un algoritmo **"Greedy" (avaro) de salto máximo**, priorizando siempre usar la menor cantidad de equipamiento posible para abaratar costos en la red.

---

## Flujo de Trabajo del Script

### 1. Inicialización y Carga del Entorno
* **Importación de GNPy:** El script comienza importando `transmission_main_example` desde la librería GNPy, lo que le permite ejecutar simulaciones físicas (cálculos de ASE, NLI, PMD, PDL, etc.) directamente en memoria sin necesidad de correr la consola del sistema repetidas veces.
* **Carga de Topología:** Lee los archivos de configuración JSON de la red y el equipamiento (`network_mashe.json` y `equipament_real_marcos_corregido.json`).
* **Mapeo con NetworkX:** Utiliza la librería de grafos `NetworkX` para reconstruir la topología de la red en memoria. Crea nodos y aristas (enlaces), y les asigna pesos basados en la distancia física (km). Esto es vital para poder trazar el ruteo original que debe seguir la luz antes de evaluar dónde colocar un regenerador.

### 2. Procesamiento del Dataset Original
Abre el archivo `resultados_gsnr_demandas_base.csv` mediante `pandas` y hace lo siguiente:
1. Agrega cuatro columnas nuevas preparadas para registrar los resultados: `Necesito_Regeneracion`, `Reg_Factible`, `Reg_Count` y `Nodos_Regeneradores`.
2. Filtra el dataset quedándose **exclusivamente con las filas donde `Factible == "NO"`**, evitando gastar tiempo de simulación en enlaces que ya demostraron ser exitosos.

### 3. Reconstrucción de la Ruta Física Completa
Para cada enlace no factible (por ejemplo, desde Mendoza hasta Chilecito), el CSV original solo muestra la ruta a nivel de ciudad: `Mendoza - San Juan - San Jose de Jachal - Patquia - Chilecito`. 

Sin embargo, GNPy necesita saber exactamente por qué fibras y amplificadores pasa la señal. Para resolver esto, el script usa `nx.shortest_path()` sobre el grafo construido en el paso 1, pasando de los nodos lógicos de ciudad, a la **ruta de componentes físicos uno a uno**, extrayendo la lista completa (Ej: *trx Mendoza -> ROADM Mendoza -> fibra_X -> ILA_Y -> fibra_Z -> ROADM San Juan*, etc.).

---

## 4. El Motor de Regeneración (`optimize_regeneration`)

Aquí ocurre la magia principal del script. Una vez que se tiene la ruta física completa, se llama a la función `optimize_regeneration()`. Esta función toma decisiones siguiendo estos pasos lógicos:

#### A. Filtrado de Nodos Candidatos
Busca en la ruta física completa aquellos nodos que sean **ROADMs** y que al mismo tiempo tengan un transceptor (`trx`) asociado en el archivo de equipamiento. Los amplificadores de línea (ILAs) son ignorados ya que no pueden regenerar la señal, solo amplificarla.

#### B. Algoritmo "Greedy" (Salto Máximo Posible)
En lugar de ir probando nodo por nodo hacia adelante, el script es "avaro". 
1. Se posiciona en el origen (ej: Mendoza).
2. Pregunta: *¿Puedo llegar hasta el destino final (ej: Chilecito) sin regenerar?*
3. Para responder, invoca a la función `run_gnpy_on_path()`, que ejecuta internamente a GNPy usando un JSON temporal recortado exclusivamente con los equipos de ese segmento.
4. Si el **GSNR retornado es mayor al Umbral OSNR** necesario para la modulación (ej: 21.5 dB para 200 Gbps), asume el salto como exitoso.
5. Si el salto falla, retrocede un ROADM intermedio y vuelve a simular: *¿Puedo llegar al menos hasta Patquía sin regenerar?*. 
6. Si vuelve a fallar, retrocede otro ROADM: *¿Puedo llegar a San José de Jachal?*. Y así sucesivamente.

Este enfoque en reversa garantiza matemáticamente que el algoritmo **siempre tomará el salto óptico más largo que las leyes de la física le permitan**, logrando así ubicar la menor cantidad posible de regeneradores.

#### C. Fallos y Tramos Inviables
Si el script está parado en un ROADM e intenta saltar al ROADM inmediatamente contiguo, pero el ruido y la atenuación de ese único tramo son tan altos que la señal no llega (GSNR < Umbral), el script dictamina el corte de la ruta. En ese punto la variable `path_possible` se vuelve `False` (Reg_Factible: NO), indicando que ni siquiera agregando un regenerador en cada ciudad es posible superar esa distancia.

### 5. Salida de Datos y Volcado al CSV
Finalmente, cuando la señal alcanza el destino o se declara como inviable, el algoritmo cuenta cuántos ROADMs intermedios requirió para lograr la conexión y cuáles fueron.

Almacena esta información en el DataFrame modificando la fila correspondiente:
* `Necesito_Regeneracion`: "SI" (Dado que el algoritmo solo procesa los que fallaron inicialmente).
* `Reg_Factible`: "SI" o "NO" (Si el algoritmo logró llegar al final).
* `Reg_Count`: Número entero con la cantidad de equipos O-E-O usados.
* `Nodos_Regeneradores`: Una cadena de texto (ej: `San Juan - Patquia`) identificando visualmente dónde deben ser instalados físicamente los regeneradores.

Todo el dataset se exporta unificado en `resultados_gsnr_demandas_base_regenerado.csv`, listo para ser inyectado en la etapa lógica (RWA/RSA).
