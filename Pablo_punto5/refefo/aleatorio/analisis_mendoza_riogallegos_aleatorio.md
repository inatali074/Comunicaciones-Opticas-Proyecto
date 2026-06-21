# Análisis de Continuidad Espectral (Aleatorio): Mendoza → Río Gallegos

## Identificación de la Demanda

| Campo | Valor |
|:---|:---|
| **Etiqueta** | `roadm Mendoza-roadm Rio Gallegos_400G_ref197` |
| **Iteración** | 197 |
| **Origen** | Mendoza |
| **Destino** | Río Gallegos |
| **Velocidad** | 400 Gbps |
| **Slots requeridos** | 6 (para 400G) |
| **Slots asignados** | **262 a 267** |
| **K-Path utilizado** | K = 4 |
| **GSNR factible** | ❌ No (asignada igualmente por disponibilidad espectral) |
| **Semilla aleatoria** | 42 |
| **Base utilizada** | `ocupacion_base_random.csv` (1077 lightpaths — con fix Cantidad de Enlaces) |

---

## Ruta Utilizada (Path_Sequence, K=4)

**Mendoza - Tunuyan - San Rafael - Malargue - Buta Ranquil - Chos Malal - Zapala - Junin de los Andes - San Martin de los Andes - Villa La Angostura - Dina Huapi - San Carlos de Bariloche - El Foyel - Epuyen - Esquel - Tecka - J. de San Martin - Alto Rio Senguer - Rio Mayo - Perito Moreno - Bajo Caracoles - Gobernador Gregores - Tres lagos - El Calafate - Esperanza (StaCruz) - Rio Gallegos**

Total: **25 saltos** (26 nodos)

> [!NOTE]
> La ruta es idéntica a la del método First-Fit (mismo K=4, priorizado por mejor GSNR). La diferencia está en la posición espectral elegida: el aleatorio elige al azar entre todas las posiciones válidas, en este caso desplazándose hasta la banda alta del espectro (slots 260+).

---

## Resultados globales del método Aleatorio (refefo)

| Métrica | Valor |
|:---|:---|
| **Demandas REFEFO totales** | 200 |
| **Asignadas con éxito** | 196 |
| **Bloqueadas** | **4** |
| **Prob. de bloqueo** | **2.00%** |
| **S_max base** | 304 |
| **S_max final** | 304 |
| **Ocupación final** | 16.44% |
| **Tiempo de ejecución** | ~3.77 seg |

> [!IMPORTANT]
> A diferencia del First-Fit (0% bloqueo), el método aleatorio bloqueó **4 demandas**. Esto ilustra claramente la mayor fragmentación espectral del método aleatorio con una base densa.

---

## Verificación de Continuidad Espectral

Se muestran los slots **S258 a S271** (ventana de contexto alrededor de los slots 262–267 asignados).

| Salto | Enlace | S258 | S259 | S260 | S261 | S262 | S263 | S264 | S265 | S266 | S267 | S268 | S269 | S270 | S271 |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | Mendoza → Tunuyan | San Jose | San Jose | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 2 | Tunuyan → San Rafael | San Jose | San Jose | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 3 | San Rafael → Malargue | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 4 | Malargue → Buta Ranquil | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 5 | Buta Ranquil → Chos Malal | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 6 | Chos Malal → Zapala | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 7 | Zapala → Junin de los Andes | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 8 | Junin de los Andes → San Martin de los Andes | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 9 | San Martin de los Andes → Villa La Angostura | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 10 | Villa La Angostura → Dina Huapi | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 11 | Dina Huapi → San Carlos de Bariloche | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 12 | San Carlos de Bariloche → El Foyel | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 13 | El Foyel → Epuyen | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 14 | Epuyen → Esquel | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 15 | Esquel → Tecka | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 16 | Tecka → J. de San Martin | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | Tecka | Tecka | Tecka | Tecka |
| 17 | J. de San Martin → Alto Rio Senguer | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 18 | Alto Rio Senguer → Rio Mayo | Alto Rio | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 19 | Rio Mayo → Perito Moreno | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 20 | Perito Moreno → Bajo Caracoles | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 21 | Bajo Caracoles → Gobernador Gregores | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 22 | Gobernador Gregores → Tres lagos | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 23 | Tres lagos → El Calafate | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 24 | El Calafate → Esperanza (StaCruz) | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 25 | Esperanza (StaCruz) → Rio Gallegos | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |

---

## Conclusión

> [!IMPORTANT]
> **Continuidad espectral verificada ✅** — Los 6 slots (262 a 267) están libres y alineados en los **25 enlaces** de la ruta K=4.

### Observaciones del contexto espectral:
- El algoritmo aleatorio eligió la posición 262 aleatoriamente (semilla 42) entre todas las ventanas de 6 slots libres simultáneamente en los 25 enlaces.

### Comparativa entre los tres métodos (demanda iter 197, Mendoza → Río Gallegos):

| Métrica | First-Fit | Aleatorio | MILP |
|:---|:---:|:---:|:---:|
| **Resultado iter 197** | ✅ ASIGNADA | ✅ ASIGNADA | (No ejecutado) |
| Slots asignados | 101 – 106 | **262 – 267** | — |
| K-Path Utilizado | K=4 | **K=4** | — |
| Prob. bloqueo REFEFO | 0.00% | **2.00%** | — |
| S_max final red | 188 | 304 | — |
