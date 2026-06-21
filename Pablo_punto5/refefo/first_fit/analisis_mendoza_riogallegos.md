# Análisis de Continuidad Espectral: Mendoza → Río Gallegos

## Identificación de la Demanda

| Campo | Valor |
|:---|:---|
| **Etiqueta** | `roadm Mendoza-roadm Rio Gallegos_400G_ref197` |
| **Iteración** | 197 |
| **Origen** | Mendoza |
| **Destino** | Río Gallegos |
| **Velocidad** | 400 Gbps |
| **Slots requeridos** | 6 (para 400G) |
| **Slots asignados** | **143 a 148** |
| **K-Path utilizado** | K = 1 |
| **GSNR factible** | ❌ No (asignada igualmente por disponibilidad espectral) |
| **Base utilizada** | `ocupacion_base_firstfit.csv` (1077 lightpaths — con fix Cantidad de Enlaces) |

---

## Ruta Utilizada (Path_Sequence, K=1)

**Mendoza - Tunuyan - San Rafael - Gral. Alvear - Santa Isabel - Victorica - Winifreda - Santa Rosa (LP) - Peru - Rio Colorado - General Conesa - San Antonio Oeste - Sierra Grande - Puerto Madryn - Trelew - Rawson - Comodoro Rivadavia - Caleta Olivia - Jaramillo - Puerto San Julian - Luis Piedrabuena - Rio Gallegos**

Total: **21 saltos** (22 nodos)

> [!NOTE]
> Esta es una ruta diferente a la del análisis anterior (base con 512 lightpaths).
> En la base anterior la ruta también era K=1 pero con 21 saltos por un camino distinto.
> Con la base actualizada, el First-Fit encontró los mismos slots libres en esta ruta.

---

## Verificación de Continuidad Espectral

Se muestran los slots **S139 a S152** (ventana de contexto alrededor de los slots 143–148 asignados).  
Los slots marcados como `**REF197**` corresponden a la demanda analizada.

| Salto | Enlace | S139 | S140 | S141 | S142 | S143 | S144 | S145 | S146 | S147 | S148 | S149 | S150 | S151 | S152 |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | Mendoza → Tunuyan | Ceres | Ceres | Ceres | Ceres | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 2 | Tunuyan → San Rafael | Ceres | Ceres | Ceres | Ceres | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 3 | San Rafael → General Alvear | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 4 | General Alvear → Santa Isabel | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 5 | Santa Isabel → Victorica | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 6 | Victorica → Winifreda | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 7 | Winifreda → Santa Rosa (LP) | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 8 | Santa Rosa (LP) → Peru | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | Santiago | Santiago | Santiago | Santiago |
| 9 | Peru → Rio Colorado | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | Santiago | Santiago | Santiago | Santiago |
| 10 | Rio Colorado → General Conesa | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | Santiago | Santiago | Santiago | Santiago |
| 11 | General Conesa → San Antonio Oeste | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | Santiago | Santiago | Santiago | Santiago |
| 12 | San Antonio Oeste → Sierra Grande | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | Santiago | Santiago | Santiago | Santiago |
| 13 | Sierra Grande → Puerto Madryn | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | Santiago | Santiago | Santiago | Santiago |
| 14 | Puerto Madryn → Trelew | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | Santiago | Santiago | Santiago | Santiago |
| 15 | Trelew → Rawson | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | Santiago | Santiago | Santiago | Santiago |
| 16 | Rawson → Comodoro Rivadavia | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | Santiago | Santiago | Santiago | Santiago |
| 17 | Comodoro Rivadavia → Caleta Olivia | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | Santiago | Santiago | Santiago | Santiago |
| 18 | Caleta Olivia → Jaramillo | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | Santiago | Santiago | Santiago | Santiago |
| 19 | Jaramillo → Puerto San Julian | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | Santiago | Santiago | Santiago | Santiago |
| 20 | Puerto San Julian → Luis Piedrabuena | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | Santiago | Santiago | Santiago | Santiago |
| 21 | Luis Piedrabuena → Rio Gallegos | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | Santiago | Santiago | Santiago | Santiago |

---

## Conclusión

> [!IMPORTANT]
> **Continuidad espectral verificada ✅** — Los 6 slots (143 a 148) están libres y alineados en los **21 enlaces** de la ruta.

### Observaciones del contexto espectral:
- **Slots 139–142** (inmediatamente anteriores): en los saltos 1–2 (Mendoza→Tunuyan→San Rafael) están ocupados por otra demanda relacionada con `Ceres`. En el resto de la ruta están libres.
- **Slots 149–152** (inmediatamente posteriores): en los saltos 8–21 están ocupados por una demanda con prefijo `Santiago`. En los saltos 1–7 están libres.
- El First-Fit eligió correctamente los slots **143–148** como el primer bloque de 6 alineado y libre en **toda** la ruta de 21 saltos.

### Comparativa con análisis anterior (base 512 lightpaths):

| Métrica | Base 512 (anterior) | Base 1077 (actual) |
|:---|:---:|:---:|
| Slots asignados | 129 – 134 | **143 – 148** |
| S_max base | 58 | 96 |
| S_max final red | 186 | 208 |
| Ocupación final | 13.85% | 15.70% |

El desplazamiento de slots (129→143) se debe a que la base actualizada tiene más lightpaths asignados en los tramos iniciales de la ruta, empujando el primer bloque libre hacia slots más altos.
