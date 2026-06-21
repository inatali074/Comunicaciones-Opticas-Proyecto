# Análisis MILP (PuLP-CBC): Mendoza → Río Gallegos — Demanda No Asignada

## Identificación de la Demanda

| Campo | Valor |
|:---|:---|
| **Etiqueta** | `roadm Mendoza-roadm Rio Gallegos_400G_ref197` |
| **Iteración** | 197 |
| **Origen** | Mendoza |
| **Destino** | Río Gallegos |
| **Velocidad** | 400 Gbps |
| **Slots requeridos** | 6 |
| **Resultado** | ❌ **BLOQUEADA** (solver sin solución factible) |
| **Base utilizada** | `ocupacion_base_milp.csv` (con fix Cantidad de Enlaces, S_max = 136) |

---

## Resultado del Solver

| Parámetro del solver | Valor |
|:---|:---|
| **Solver** | CBC (via PuLP) |
| **Tiempo límite** | 120 segundos |
| **Gap relativo** | 5% |
| **Estado final** | `Not Solved` |
| **Cota inferior (lower bound)** | 136 |
| **Nodos explorados** | 11,217 |
| **Iteraciones LP** | 277,278 |
| **Solución factible encontrada** | ❌ No |

> [!WARNING]
> El solver CBC exploró más de **11,000 nodos** del árbol de branch-and-bound sin encontrar ninguna solución entera factible dentro del límite de 120 segundos. El modelo tiene 3,898 variables y 7,594 restricciones, lo que lo hace computacionalmente intratable en ese tiempo.

---

## Resultados Globales del Método MILP (refefo)

| Métrica | Valor |
|:---|:---|
| **Demandas REFEFO totales** | 200 |
| **Demandas con posiciones válidas** | 200 |
| **Demandas pre-bloqueadas** | 0 |
| **Asignadas con éxito** | **0** |
| **Bloqueadas** | **200** |
| **Prob. de bloqueo** | **100.00%** |
| **S_max base** | 136 |
| **S_max final** | 136 (sin cambios) |
| **Ocupación final** | 5.22% (igual a la base) |
| **Tiempo de ejecución** | 120.00 seg |

> [!NOTE]
> El CSV exportado (`ocupacion_refefo_pulp.csv`) contiene únicamente el estado base sin ninguna demanda REFEFO asignada. Esto es el comportamiento esperado por diseño: si el solver no alcanza optimalidad, se bloquean todas las demandas para mantener un modelo conservador.

---

## Análisis de la Complejidad del Modelo

| Componente | Cantidad |
|:---|:---|
| Variables continuas/enteras (s[d]) | 200 |
| Variable S_max | 1 |
| Variables binarias de base (z) | 409 |
| Variables binarias de solapamiento (x) | 3,288 |
| **Total variables** | **3,898** |
| **Total restricciones** | **7,594** |

Con 1077 lightpaths base (vs. 512 anteriores), la densidad espectral aumenta, generando más rangos prohibidos y más variables binarias de base, lo que dificulta aún más la convergencia del solver.

---

## Comparativa entre los Tres Métodos (demanda iter 197, Mendoza → Río Gallegos, 400G)

| Métrica | First-Fit | Aleatorio | MILP |
|:---|:---:|:---:|:---:|
| **Resultado** | ✅ ASIGNADA | ✅ ASIGNADA | ❌ BLOQUEADA |
| **Slots asignados** | 143 – 148 | 111 – 116 | — |
| **K-Path usado** | K = 1 | K = 1 | — |
| **S_max base** | 96 | 304 | 136 |
| **S_max final red** | 208 | 304 | 136 |
| **Prob. bloqueo total REFEFO** | **0.00%** | **1.00%** | **100.00%** |
| **Tiempo de ejecución** | < 1 seg | 1.55 seg | 120 seg |
| **Ocupación final** | 15.70% | 15.49% | 5.22% |

### Conclusión comparativa:

- **First-Fit** es el método más eficiente: 0% bloqueo, S_max compacto (208), ejecución casi instantánea.
- **Aleatorio** tiene 1.00% de bloqueo (2 demandas), S_max máximo (304) por la fragmentación inherente, pero es rápido.
- **MILP** no logra asignar ninguna demanda en 120s por la complejidad del modelo (~3,900 variables binarias). El resultado es conservador pero no útil en la práctica con estos tiempos.

> [!TIP]
> Para mejorar el MILP, se podría aplicar un **warm-start con la solución de First-Fit** como valores iniciales de las variables `s[d]`, lo que daría al solver una cota superior ajustada desde el inicio y potencialmente permitiría encontrar una solución factible rápidamente.
