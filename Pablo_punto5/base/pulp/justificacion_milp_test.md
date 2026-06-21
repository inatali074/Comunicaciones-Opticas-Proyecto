# Justificación del Caso de Prueba MILP Reducido (Actualizado con Bloqueo)

## Contexto

El script `asignacion_pulp.py` implementa una formulación MILP exacta para el problema de **Ruteo y Asignación de Espectro (RSA)** en la red ARSAT. El modelo completo (1077 lightpaths, 304 slots) resulta computacionalmente intratable para el solver CBC dentro de límites de tiempo razonables.

Para validar el comportamiento del modelo matemático tanto en condiciones de factibilidad como de saturación (probabilidad de bloqueo del 100%), se ha configurado un **caso de prueba reducido y sobre-explotado**.

---

## Parámetros del Caso de Prueba Actualizado

| Parámetro | Valor completo | Valor test (Óptimo) | Valor test (Con Bloqueo) | Constante en código |
|:---|:---:|:---:|:---:|:---|
| Filas CSV (demandas únicas) | 512 | 50 | **150** | `N_ROWS_TEST = 150` |
| Slots de la grilla | 304 | 152 | **30** | `TOTAL_SLOTS = 30` |
| Velocidades incluidas | todas | todas | **todas** | (sin cambio) |
| Tiempo límite solver | 120 s | 120 s | **120 s** | `TIME_LIMIT = 120` |
| Lightpaths expandidos | 1077 | 104 | **318** | (automático) |
| Variables binarias x | ~58,000 | ~484 | **1,385** | (automático) |
| Archivo de salida | `ocupacion_base_milp.csv` | `ocupacion_base_milp_test.csv` | **`ocupacion_base_milp_test.csv`** | `OUTPUT_FILE` |

---

## Justificación de los Cambios para Generar Bloqueo

### 1. `N_ROWS_TEST = 150` (318 Lightpaths)

Para incrementar la carga en la red y tener una cantidad representativa de demandas que compartan enlaces físicos, aumentamos a las primeras 150 demandas de la base. Esto eleva los lightpaths a **318**, multiplicando la cantidad de intersecciones de rutas en el modelo (lo que genera **1,385 variables de solapamiento binarias `x`**).

### 2. `TOTAL_SLOTS = 30` (Reducción Estructural de la Grilla)

El solver de optimización matemática para ruteo de espectro (RSA) requiere asignar bloques continuos de slots (de tamaño 4 o 6 según el ancho de banda). Si la capacidad física espectral de los enlaces es muy baja, se vuelve matemáticamente imposible ubicar todas las demandas simultáneamente en sus respectivas rutas sin que choquen.

*   Al correr con **150 filas** y **152 slots**, el solver CBC convergió a una solución óptima con $S_{max} = 64$ en 120s (0% de bloqueo).
*   Al reducir el límite espectral físico de la grilla a **30 slots** (`TOTAL_SLOTS = 30`), el límite superior disponible es estrictamente menor a la cota óptima requerida por el cuello de botella físico de la red ($30 < 64$).
*   Esto garantiza por definición la **infactibilidad matemática** del problema, obligando al optimizador a reportar un estado de `Not Solved` (No Resuelto) y marcando la probabilidad de bloqueo en el **100%**.

---

## Resultados Obtenidos en la Corrida

*   **Estado final del solver**: `Not Solved` (Infactible dentro del límite espectral de 30 slots)
*   **Tiempo de cómputo**: 120.10 segundos
*   **Demandas cargadas**: 150 (318 lightpaths)
*   **Probabilidad de Bloqueo**: **100.00%** (todas las demandas base son rechazadas para mantener el modelo coherente y seguro).
*   **Matriz exportada**: `ocupacion_base_milp_test.csv` (grilla vacía de 30 slots).
