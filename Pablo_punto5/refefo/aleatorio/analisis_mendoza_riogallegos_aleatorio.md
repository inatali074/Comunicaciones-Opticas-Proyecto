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
| **Slots asignados** | **111 a 116** |
| **K-Path utilizado** | K = 1 |
| **GSNR factible** | ❌ No (asignada igualmente por disponibilidad espectral) |
| **Semilla aleatoria** | 42 |
| **Base utilizada** | `ocupacion_base_random.csv` (1077 lightpaths — con fix Cantidad de Enlaces) |

---

## Ruta Utilizada (Path_Sequence, K=1)

**Mendoza - Tunuyan - San Rafael - Gral. Alvear - Santa Isabel - Victorica - Winifreda - Santa Rosa (LP) - Peru - Rio Colorado - General Conesa - San Antonio Oeste - Sierra Grande - Puerto Madryn - Trelew - Rawson - Comodoro Rivadavia - Caleta Olivia - Jaramillo - Puerto San Julian - Luis Piedrabuena - Rio Gallegos**

Total: **21 saltos** (22 nodos)

> [!NOTE]
> La ruta es idéntica a la del método First-Fit (mismo K=1). La diferencia está en la posición espectral elegida: el aleatorio elige al azar entre todas las posiciones válidas, mientras que First-Fit toma siempre la primera disponible.

---

## Resultados globales del método Aleatorio (refefo)

| Métrica | Valor |
|:---|:---|
| **Demandas REFEFO totales** | 200 |
| **Asignadas con éxito** | 198 |
| **Bloqueadas** | **2** |
| **Prob. de bloqueo** | **1.00%** |
| **S_max base** | 304 |
| **S_max final** | 304 |
| **Ocupación final** | 15.49% |
| **Tiempo de ejecución** | 1.55 seg |

> [!IMPORTANT]
> A diferencia del First-Fit (0% bloqueo), el método aleatorio bloqueó **2 demandas** (iter 175: Tres lagos → Ituzaingo, 300G). Esto ilustra la mayor fragmentación espectral del método aleatorio con una base densa.

---

## Verificación de Continuidad Espectral

Se muestran los slots **S107 a S120** (ventana de contexto alrededor de los slots 111–116 asignados).

| Salto | Enlace | S107 | S108 | S109 | S110 | S111 | S112 | S113 | S114 | S115 | S116 | S117 | S118 | S119 | S120 |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | Mendoza → Tunuyan | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 2 | Tunuyan → San Rafael | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 3 | San Rafael → General Alvear | San Rafa | San Rafa | San Rafa | San Rafa | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 4 | General Alvear → Santa Isabel | San Rafa | San Rafa | San Rafa | San Rafa | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 5 | Santa Isabel → Victorica | San Rafa | San Rafa | San Rafa | San Rafa | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 6 | Victorica → Winifreda | San Rafa | San Rafa | San Rafa | San Rafa | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 7 | Winifreda → Santa Rosa (LP) | San Rafa | San Rafa | San Rafa | San Rafa | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 8 | Santa Rosa (LP) → Peru | San Rafa | San Rafa | San Rafa | San Rafa | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | Cañada D | Cañada D | Cañada D |
| 9 | Peru → Rio Colorado | San Rafa | San Rafa | San Rafa | San Rafa | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | Cañada D | Cañada D | Cañada D |
| 10 | Rio Colorado → General Conesa | General | General | General | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | Cañada D | Cañada D | Cañada D |
| 11 | General Conesa → San Antonio Oeste | General | General | General | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | Cañada D | Cañada D | Cañada D |
| 12 | San Antonio Oeste → Sierra Grande | General | General | General | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | Cañada D | Cañada D | Cañada D |
| 13 | Sierra Grande → Puerto Madryn | General | General | General | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | Cañada D | Cañada D | Cañada D |
| 14 | Puerto Madryn → Trelew | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | Cañada D | Cañada D | Cañada D |
| 15 | Trelew → Rawson | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | Cañada D | Cañada D | Cañada D |
| 16 | Rawson → Comodoro Rivadavia | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 17 | Comodoro Rivadavia → Caleta Olivia | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 18 | Caleta Olivia → Jaramillo | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 19 | Jaramillo → Puerto San Julian | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 20 | Puerto San Julian → Luis Piedrabuena | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 21 | Luis Piedrabuena → Rio Gallegos | Luis Pie | Luis Pie | Luis Pie | Luis Pie | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |

---

## Conclusión

> [!IMPORTANT]
> **Continuidad espectral verificada ✅** — Los 6 slots (111 a 116) están libres y alineados en los **21 enlaces** de la ruta.

### Observaciones del contexto espectral:
- **Slots 107–110** (anteriores): parcialmente ocupados por demandas como `San Rafael...` (saltos 3–9) y `General Conesa...` (saltos 10–13) y `Luis Piedrabuena...` (salto 21).
- **Slots 117–120** (posteriores): ocupados por `Cañada De Gómez...` en saltos 8–15.
- El algoritmo aleatorio eligió la posición 111 aleatoriamente (semilla 42) entre todas las ventanas de 6 slots libres simultáneamente en los 21 enlaces.

### Comparativa entre los tres métodos (demanda iter 197, Mendoza → Río Gallegos):

| Métrica | First-Fit | Aleatorio | MILP |
|:---|:---:|:---:|:---:|
| **Resultado iter 197** | ✅ ASIGNADA | ✅ ASIGNADA | ❌ BLOQUEADA |
| Slots asignados | 143 – 148 | **111 – 116** | — |
| S_max base | 96 | 304 | 136 |
| Prob. bloqueo REFEFO | 0.00% | **1.00%** | **100.00%** |
| S_max final red | 208 | 304 | 136 |
