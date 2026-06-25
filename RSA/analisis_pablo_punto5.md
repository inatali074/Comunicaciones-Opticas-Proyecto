# Análisis Detallado de los Algoritmos de Asignación de Espectro (`Pablo_punto5`)

Este documento presenta una devolución técnica detallada y un análisis crítico de los tres archivos de simulación de asignación de espectro ubicados en la carpeta `Pablo_punto5`:
1. `asignacion_aleatorio.py`
2. `asignacion_first_fit.py`
3. `asignacion_pulp.py`

---

## 1. Resumen Ejecutivo
Los tres scripts implementan algoritmos para resolver el problema de **Ruteo y Asignación de Espectro (RSA)** en una red elástica de fibra óptica (EON) utilizando como base la topología y demandas de ARSAT (512 demandas de tráfico). 

Cada script aborda el problema con una estrategia distinta:
* **Aleatorio**: Busca todas las posiciones espectrales contiguas y alineadas en la ruta y selecciona una al azar.
* **First-Fit (Greedy)**: Selecciona el primer bloque de slots libres (de izquierda a derecha) que sea contiguo y alineado en toda la ruta.
* **MILP (PuLP-CBC)**: Formulación de Programación Lineal Entera Mixta para minimizar el slot máximo utilizado en la red ($S_{max}$).

---

## 2. Análisis Individual de los Archivos

### 📄 `asignacion_aleatorio.py`
* **Metodología**: Escanea secuencialmente los 304 slots de la grilla Flexi-Grid para identificar ventanas continuas libres del tamaño requerido por la demanda en todos los enlaces de la ruta. De la lista de índices válidos, elige uno mediante `random.choice()`.
* **Aspectos Destacados**:
  * **Reproducibilidad**: Se fija correctamente la semilla `random.seed(42)` en la línea 7, garantizando que el comportamiento sea determinista entre corridas de prueba.
  * **Modelado Direccional**: Los enlaces se gestionan en forma de tuplas direccionadas `(origen, destino)`, permitiendo separar físicamente los recursos espectrales en ambas direcciones de una misma conexión física.
* **Limitaciones**:
  * **Fragmentación**: La asignación aleatoria sobre un espectro vacío no muestra problemas para la demanda base (0% de bloqueo), pero bajo tráfico dinámico o mayor carga tiende a fragmentar severamente el espectro, reduciendo la eficiencia general de la red.

---

### 📄 `asignacion_first_fit.py`
* **Metodología**: Implementa la heurística First-Fit clásico. Asigna la demanda en el índice de espectro libre más bajo disponible de forma alineada en todos los enlaces de su ruta.
* **Aspectos Destacados**:
  * **Compensación y Compresión**: Funciona de forma excelente. Al compactar las demandas hacia la parte inferior del espectro, libera slots contiguos de gran tamaño a la derecha para futuras demandas de alta velocidad.
  * **Eficiencia Temporal**: Se ejecuta casi instantáneamente (menos de 0.2 segundos) para las 512 demandas.
* **Detalles a corregir / observaciones**:
  * **Falta de medición de tiempo**: Aunque el script principal calcula estadísticas, no importa el módulo `time` ni muestra el tiempo de ejecución en consola, a diferencia del script aleatorio.
  * **Formato de Exportación**: Exporta a `ocupacion_base_firstfit.csv`. Los nombres de las columnas identificadoras son `Nodo_Origen` y `Nodo_Destino`. 
    > [!IMPORTANT]
    > En el código de Mateo (`Mateo_punto5/codigo_first_fit.py`), las columnas se llaman `Source` y `Destination`. Es necesario unificar este formato si otros scripts (como cálculos de GSNR o fragmentación) leen este CSV y esperan nombres en inglés o español.

---

### 📄 `asignacion_pulp.py`
* **Metodología**: Modela el RSA como un problema de optimización exacta MILP para minimizar el slot máximo utilizado ($S_{max}$). Define variables enteras para el slot de inicio de cada demanda y variables binarias $x_{(d1, d2)}$ para evitar el solapamiento de espectro si comparten algún tramo físico de fibra.
* **Puntos Críticos y Bugs Detectados**:

#### 1. El Bug de la Constante Big-M (`M = 304`) ⚠️
En la formulación matemática de no-solapamiento (líneas 120-126):
```python
prob += s[d1["id"]] + d1["slots"] <= s[d2["id"]] + M * (1 - var_binaria)
prob += s[d2["id"]] + d2["slots"] <= s[d1["id"]] + M * var_binaria
```
La constante $M$ debe ser un número estrictamente mayor que la diferencia máxima posible entre las variables del modelo. Si $var\_binaria = 1$ (lo que implica que la demanda 1 va antes que la demanda 2), la segunda ecuación exige:
$$s[d_2] + d_2["slots"] \le s[d_1] + M$$
Si colocamos la demanda 2 cerca del final del espectro ($s[d_2] = 300$, $d_2["slots"] = 6$) y la demanda 1 al principio ($s[d_1] = 0$), obtenemos:
$$306 \le 0 + 304 \implies 306 \le 304 \quad \mathbf{(Falso)}$$
Esto significa que el modelo **bloquea artificialmente** ciertas combinaciones válidas de asignación porque $M$ es demasiado pequeño. 
* **Solución**: Aumentar $M$ a un valor seguro como `M = 500` o `M = 1000`.

#### 2. Descarte Incondicional de Soluciones Factibles 🛑
En la línea 156 se evalúa la exportación:
```python
if pulp.LpStatus[status] == "Optimal":
    # Lógica de guardado...
```
El resolvedor por defecto (CBC) tiene un límite de tiempo de 600 segundos. Si el tiempo expira y el resolvedor no ha **demostrado matemáticamente** la optimalidad absoluta (aunque tenga una solución factible muy buena en memoria), el status devuelto por PuLP puede ser `Not Solved` o `Undefined`. 
Al requerir estrictamente el estado `"Optimal"`, el script:
1. Reporta falsamente **100% de Probabilidad de Bloqueo** en consola.
2. Exporta una matriz **completamente vacía** (con strings vacíos `""`) en `ocupacion_base_milp.csv`.
* **Solución**: Modificar la condición para que verifique si `pulp.value(S_max)` o las variables tienen valores válidos asignados, permitiendo exportar soluciones factibles subóptimas obtenidas antes del timeout.

#### 3. Tiempos de Cómputo Inviables (Complejidad del Modelo) ⏳
El modelo genera **1,731 variables binarias** de solapamiento y más de **3,900 restricciones**. Al no tener configurada una tolerancia de brecha (Gap Relativo), el solver CBC busca exhaustivamente hasta el final. En la práctica, esto causa que el script corra durante los 10 minutos enteros sin exportar resultados útiles.
* **Solución**: Introducir parámetros de parada rápida en el solver como `gapRel=0.05` (5% de tolerancia con respecto al límite inferior teórico) y un `timeLimit` acotado (ej. 60 o 120 segundos).

---

## 3. Comparativa de Modelado de Enlaces (Pablo vs. Mateo)

Existe una diferencia conceptual clave sobre cómo se interpretan los enlaces físicos en los dos directorios:

| Característica | Modelo de Pablo (`Pablo_punto5`) | Modelo de Mateo (`Mateo_punto5`) |
| :--- | :--- | :--- |
| **Tratamiento del enlace** | **Direccional**: `(Origen, Destino)` se mantiene tal cual. | **Bidireccional Ordenado**: Ordena alfabéticamente los nombres para crear una clave única. |
| **Consecuencia en Enlaces** | Genera **237 enlaces únicos**. Un enlace A $\to$ B y B $\to$ A tienen espectros independientes. | Genera **225 enlaces únicos**. Un enlace A $\to$ B y B $\to$ A comparten la misma grilla espectral. |
| **Interpretación Física** | Asume fibra dúplex (dos fibras físicas por tramo, una para ida y otra para vuelta). | Asume fibra símplex o recursos espectrales compartidos bidireccionalmente en un solo hilo. |

> [!NOTE]
> El modelo de Pablo (Direccional) es técnicamente más preciso para sistemas terrestres interurbanos tradicionales (donde se instalan pares de fibras). Además, el modelo de Mateo restringe el espectro a la mitad al obligar a los tráficos de ida y vuelta a competir por los mismos slots físicos.

---

## 4. Tabla Comparativa de Resultados (Tráfico Base - 512 Demandas)

A partir de las pruebas de ejecución realizadas directamente sobre la base de datos real `Demanda_Base - Tráfico base.csv`, se obtuvieron los siguientes resultados:

| Métrica | Método Aleatorio | Método First-Fit | Método MILP (PuLP-CBC)* |
| :--- | :--- | :--- | :--- |
| **Tiempo de Ejecución** | ~0.15 segundos | ~0.13 segundos | ~60 segundos (con Gap 5%) |
| **Slot Máximo Utilizado ($S_{max}$)**| 304 (ocupa todo el rango) | **58** (excelente compactación) | **94** (truncado a los 60s) |
| **Probabilidad de Bloqueo** | 0.00% | 0.00% | 0.00% (con corrección de status) |
| **Estado del archivo final** | Completo (`ocupacion_base_random.csv`) | Completo (`ocupacion_base_firstfit.csv`) | Completo (`ocupacion_base_milp.csv`)* |

*\* Nota: El resultado de MILP se obtuvo aplicando las mejoras sugeridas para evitar el bloqueo de exportación por timeout.*

### Conclusión del Rendimiento:
Para este conjunto de datos, **First-Fit es ampliamente superior a un MILP truncado**. Debido a la baja carga de la red (solo requiere un máximo de 58 slots), First-Fit resuelve el problema de manera óptima y en una fracción de segundo, mientras que el solver exacto requiere mucha potencia de cómputo y, al ser detenido prematuramente, entrega una cota peor ($S_{max} = 94$).

---

## 5. Recomendaciones de Mejora para el Código de Pablo

Si se desea corregir y potenciar el código de `asignacion_pulp.py`, se sugiere aplicar los siguientes cambios estructurales:

### A. Corrección de Parámetros del Solver y Guardado
Reemplazar la llamada al solver por una que incluya `gapRel` y corregir la condición de escritura del CSV para aceptar soluciones factibles no óptimas:

```python
# 1. Configurar límites razonables de parada
status = prob.solve(pulp.PULP_CBC_CMD(msg=True, timeLimit=60, gapRel=0.05))

# 2. Extraer valor y comprobar existencia física de la solución
s_max_val = pulp.value(S_max)
if s_max_val is not None:
    print(f"Slot máximo alcanzado en la red (S_max): {int(s_max_val)}")
    prob_bloqueo = 0.0
else:
    print("El optimizador no pudo encontrar ninguna solución factible.")
    prob_bloqueo = 100.0
```

### B. Inicialización en Caliente (Warm Start)
Para acelerar drásticamente el modelo matemático, se puede inyectar la solución encontrada por First-Fit como valores iniciales para las variables `s[d]`. Esto le da al solver CBC una cota inicial muy ajustada ($S_{max} = 58$) reduciendo drásticamente el árbol de búsqueda de branch-and-bound.
