# Reporte de Métricas de Calidad de Red - RSA (First-Fit vs. Aleatorio)

Este reporte presenta, compara y analiza los parámetros de calidad de red obtenidos para las simulaciones de ruteo y asignación de espectro (RSA) utilizando dos políticas distintas de asignación de slots: **First-Fit** y **Aleatorio (Random)**. Se evalúan ambos métodos bajo el escenario de **Tráfico Base** (1077 demandas de luz) y el escenario acumulativo incremental de **Tráfico REFEFO** (200 demandas de luz adicionales).

---

## 1. Definición Teórica de las Métricas

Para evaluar exhaustivamente el desempeño de la grilla flexible de la red (304 slots de 12.5 GHz por fibra, bidireccional), se implementaron las siguientes métricas en ambos algoritmos:

### A. Tiempos de Ruteo y Asignación por Demanda
Mide el tiempo de cómputo en milisegundos ($ms$) requerido por el algoritmo para resolver la demanda individual:
- **Tráfico Base**: Incluye la resolución de nombres, el algoritmo de ruteo BFS y la asignación en la grilla.
- **Tráfico REFEFO**: Incluye el ordenamiento por mejor GSNR, el intento secuencial sobre los K-caminos alternativos ordenados y la asignación espectral.

### B. Probabilidad de Bloqueo por Enlace Físico
Calcula de forma desagregada la tasa de bloqueo experimentada enlace por enlace:
$$P_{\text{bloqueo}}(e) = \frac{N_{\text{block}}(e)}{N_{\text{req}}(e)}$$
Donde $N_{\text{req}}(e)$ es la cantidad de demandas que solicitaron pasar por el enlace $e$ (en su ruta elegida si fue exitosa, o en su ruta preferida principal si se bloqueó), y $N_{\text{block}}(e)$ es la cantidad de veces que el enlace impidió la asignación debido a falta de espectro continuo.

### C. Fragmentación Espectral ($F$)
Mide qué tan segmentado queda el espectro libre en cada enlace físico:
$$F(e) = \begin{cases} 1 - \frac{M_{\text{libre}}(e)}{S_{\text{libres}}(e)} & \text{si } S_{\text{libres}}(e) > 0 \\ 1.0 & \text{si } S_{\text{libres}}(e) = 0 \end{cases}$$
Donde $M_{\text{libre}}(e)$ es el tamaño (en slots) del bloque libre continuo más grande del enlace $e$, y $S_{\text{libres}}(e)$ es el número total de slots libres en ese enlace. 
- $F = 0.0$ indica espectro libre totalmente contiguo (ideal).
- $F \to 1.0$ indica espectro pulverizado en bloques pequeños que no pueden albergar nuevas demandas de alta velocidad.

### D. Contigüidad del Espectro ($C$)
Evalúa la distribución de los bloques libres en la grilla de cada fibra mediante un índice cuadrático:
$$C(e) = \begin{cases} \frac{\sum_{j=1}^{k} s_j^2}{S_{\text{libres}}^2} & \text{si } S_{\text{libres}}(e) > 0 \\ 0.0 & \text{si } S_{\text{libres}}(e) = 0 \end{cases}$$
Donde $s_j$ es el tamaño de cada bloque libre contiguo $j$ en el enlace $e$.
- $C = 1.0$ representa contigüidad perfecta (un único bloque libre gigante).
- $C \to 0.0$ representa bloques libres extremadamente dispersos.

### E. Transiciones Ocupado-a-Libre ($T_{\text{occ}\to\text{free}}$)
Mide la cantidad de variaciones o cambios de estado desde un slot ocupado hacia un slot libre al recorrer secuencialmente los 304 slots de cada grilla física:
$$T_{\text{occ}\to\text{free}}(e) = \sum_{i=1}^{303} \mathbb{I}(\text{slot } i-1 \text{ ocupado y slot } i \text{ libre})$$
Donde $\mathbb{I}$ es la función indicadora. 
- Un valor bajo de transiciones refleja un espectro ordenado donde los slots ocupados están agrupados (típicamente al inicio de la grilla en First-Fit), dejando bloques libres compactos.
- Un valor alto refleja alternancia continua (efecto "serrucho") entre slots ocupados y libres, fragmentando la grilla.
Se computa el valor **mínimo**, **máximo** y **promedio** de estas transiciones sobre el conjunto de todos los enlaces de la red.

### F. Variación y Equidad de la Carga por Enlace
Representa la diferencia de uso de espectro (slots ocupados $U(e) \in [0, 304]$) entre las fibras de la red:
- **Variación de Carga**: $\Delta U = \max_e U(e) - \min_e U(e)$
- **Ocupación Promedio**: $\text{Promedio}(U(e))$

---

## 2. Tabla Comparativa de Resultados Globales

A continuación se consolidan los valores globales promedio y límites de las métricas obtenidos en las simulaciones de ambos métodos:

| Métrica / Parámetro Global | First-Fit (Base) | Aleatorio (Base) | First-Fit (REFEFO Acum.) | Aleatorio (REFEFO Acum.) |
| :--- | :---: | :---: | :---: | :---: |
| **Lightpaths procesados** | 1077 | 1077 | 1077 + 200 | 1077 + 200 |
| **Lightpaths asignados** | 1077 | 1075 | 1277 | 1252 |
| **Lightpaths bloqueados** | 0 (0.00%) | 2 (0.19%) | 0 (0.00%) | 23 (11.50% en REFEFO) |
| **Tiempo de cómputo promedio** | **0.6446 ms** | **1.2575 ms** | **13.0005 ms** | **13.4467 ms** |
| **Ocupación promedio de slots** | 37.08 (12.20%) | 36.08 (11.87%) | 76.96 (25.31%) | 63.77 (20.98%) |
| **Carga mínima en enlace** | 4 slots | 4 slots | 4 slots | 0 slots |
| **Carga máxima en enlace** | 96 slots | 88 slots | 202 slots | 156 slots |
| **Variación de carga ($\Delta U$)** | 92 slots | 84 slots | 198 slots | 156 slots |
| **Fragmentación prom. de red ($F$)**| **0.0211** | **0.6561** | **0.3973** | **0.7482** |
| **Contigüidad prom. de red ($C$)** | **0.9614** | **0.2323** | **0.4472** | **0.1541** |
| **Bloque libre máx. promedio** | 261.47 slots | 94.11 slots | 137.12 slots | 62.53 slots |
| **Transiciones Ocupado $\to$ Libre** | **1.44** (1 - 5) | **8.31** (1 - 19) | **6.52** (1 - 14) | **13.06** (0 - 27) |
| **Prob. bloqueo prom. enlace** | 0.00% | 1.11% | 0.00% | 10.26% |

*Nota: Los valores entre paréntesis en la fila de transiciones corresponden al rango `(mínimo - máximo)` registrado entre todos los enlaces.*

---

## 3. Análisis Técnico del Impacto de la Asignación en la Fragmentación

### 1. Dinámica de Transiciones y Estructura Espectral
El conteo de transiciones Ocupado-a-Libre ($T_{\text{occ}\to\text{free}}$) constituye un excelente indicador de la dispersión de slots:
- **First-Fit (Base: $1.44$ | REFEFO: $6.52$ promedio)**: Al asignar siempre sobre el primer slot indexado libre de izquierda a derecha, First-Fit empaqueta firmemente el espectro. En el escenario base, la gran mayoría de los enlaces tienen exactamente **1** transición (un bloque continuo ocupado a la izquierda, y un gran bloque libre a la derecha). En el escenario REFEFO incremental, a pesar de la mayor carga de tráfico, las transiciones se contienen en un promedio de **6.52** por enlace (con un máximo de 14).
- **Aleatorio (Base: $8.31$ | REFEFO: $13.06$ promedio)**: Al escoger posiciones aleatorias en la grilla para cada demanda, el método aleatorio distribuye los bloques ocupados por todo el enlace de forma no compacta. Esto dispara las transiciones promedio a **13.06** (llegando a registrarse hasta **27** variaciones en los enlaces más críticos). Esto evidencia físicamente que la grilla libre ha sido fracturada en multitud de pequeños segmentos dispersos de espectro inutilizable.

### 2. Relación de Transiciones con Fragmentación ($F$), Contigüidad ($C$) y Bloqueo
Las transiciones altas repercuten directamente en las métricas clásicas y provocan bloqueos:
- Con **8.31** transiciones base (Aleatorio), el tamaño promedio del bloque libre máximo cae drásticamente de **261.47 slots** (First-Fit) a **94.11 slots** (Aleatorio), con una fragmentación promedio de **0.6561**.
- Al sumarse el tráfico REFEFO, la contigüidad cuadrática bajo el método aleatorio cae a un crítico **0.1541** y el bloque libre máximo promedio se reduce a apenas **62.53 slots**. 
- Esta degradación espectral (representada por el elevado promedio de **13.06** transiciones) explica por qué el algoritmo Aleatorio bloquea **23** demandas adicionales de REFEFO ($11.50\%$), mientras que First-Fit aloja el 100% de las solicitudes con **0.00%** de bloqueo acumulado.

---

## 4. Directorio de Reportes Detallados por Enlace

Para inspeccionar las métricas de calidad enlace por enlace en cada método (incluyendo el conteo individual de transiciones $T_{\text{occ}\to\text{free}}$), se pueden consultar los siguientes archivos generados en las carpetas de RSA:

### Método First-Fit
- **Tráfico Base (Py)**: [reporte_base_firstfit_V3_metricas.txt](file:///home/maximo/opticas/TpOpticas/RSA/base/first_fit/py/reporte_base_firstfit_V3_metricas.txt)
- **Tráfico REFEFO (first_fit)**: [reporte_refefo_firstfit_metricas.txt](file:///home/maximo/opticas/TpOpticas/RSA/refefo/first_fit/reporte_refefo_firstfit_metricas.txt)
- **Matriz Base (Py)**: [ocupacion_base_firstfit_V3_metricas.csv](file:///home/maximo/opticas/TpOpticas/RSA/base/first_fit/py/ocupacion_base_firstfit_V3_metricas.csv)
- **Matriz REFEFO (first_fit)**: [ocupacion_refefo_firstfit_metricas.csv](file:///home/maximo/opticas/TpOpticas/RSA/refefo/first_fit/ocupacion_refefo_firstfit_metricas.csv)

### Método Aleatorio (Random)
- **Tráfico Base (aleatorio)**: [reporte_base_random_V3_metricas.txt](file:///home/maximo/opticas/TpOpticas/RSA/base/aleatorio/reporte_base_random_V3_metricas.txt)
- **Tráfico REFEFO (aleatorio)**: [reporte_refefo_random_metricas.txt](file:///home/maximo/opticas/TpOpticas/RSA/refefo/aleatorio/reporte_refefo_random_metricas.txt)
- **Matriz Base (aleatorio)**: [ocupacion_base_random_V3_metricas.csv](file:///home/maximo/opticas/TpOpticas/RSA/base/aleatorio/ocupacion_base_random_V3_metricas.csv)
- **Matriz REFEFO (aleatorio)**: [ocupacion_refefo_random_metricas.csv](file:///home/maximo/opticas/TpOpticas/RSA/refefo/aleatorio/ocupacion_refefo_random_metricas.csv)
