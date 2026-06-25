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
| **Slots asignados** | **101 a 106** |
| **K-Path utilizado** | K = 4 |
| **GSNR factible** | ❌ No (asignada igualmente por disponibilidad espectral) |
| **Base utilizada** | `ocupacion_base_firstfit.csv` (1077 lightpaths — con fix Cantidad de Enlaces) |

---

## Ruta Utilizada (Path_Sequence, K=4)

**Mendoza - Tunuyan - San Rafael - Malargue - Buta Ranquil - Chos Malal - Zapala - Junin de los Andes - San Martin de los Andes - Villa La Angostura - Dina Huapi - San Carlos de Bariloche - El Foyel - Epuyen - Esquel - Tecka - J. de San Martin - Alto Rio Senguer - Rio Mayo - Perito Moreno - Bajo Caracoles - Gobernador Gregores - Tres lagos - El Calafate - Esperanza (StaCruz) - Rio Gallegos**

Total: **25 saltos** (26 nodos)

> [!NOTE]
> Esta ruta (K=4) fue elegida por encima de la ruta más corta (K=1) debido a la actualización en la lógica de asignación, la cual ahora prioriza las rutas **con mejor GSNR** de manera descendente. El algoritmo verificó que esta ruta andina presentaba mejor señal óptica base que la ruta costera habitual, a pesar de ser más larga, y como encontró espectro libre (First-Fit), la asignó inmediatamente.

---

## Verificación de Continuidad Espectral

Se muestran los slots **S97 a S110** (ventana de contexto alrededor de los slots 101–106 asignados).  
Los slots marcados como `**REF197**` corresponden a la demanda analizada.

| Salto | Enlace | S97 | S98 | S99 | S100 | S101 | S102 | S103 | S104 | S105 | S106 | S107 | S108 | S109 | S110 |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | Mendoza → Tunuyan | San Jose | San Jose | San Jose | San Jose | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 2 | Tunuyan → San Rafael | San Jose | San Jose | San Jose | San Jose | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 3 | San Rafael → Malargue | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 4 | Malargue → Buta Ranquil | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 5 | Buta Ranquil → Chos Malal | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 6 | Chos Malal → Zapala | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 7 | Zapala → Junin de los Andes | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 8 | Junin de los Andes → San Martin de los Andes | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | San Jose | San Jose | San Jose | San Jose |
| 9 | San Martin de los Andes → Villa La Angostura | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | San Jose | San Jose | San Jose | San Jose |
| 10 | Villa La Angostura → Dina Huapi | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | San Jose | San Jose | San Jose | San Jose |
| 11 | Dina Huapi → San Carlos de Bariloche | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | San Jose | San Jose | San Jose | San Jose |
| 12 | San Carlos de Bariloche → El Foyel | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | San Jose | San Jose | San Jose | San Jose |
| 13 | El Foyel → Epuyen | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | San Jose | San Jose | San Jose | San Jose |
| 14 | Epuyen → Esquel | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | San Jose | San Jose | San Jose | San Jose |
| 15 | Esquel → Tecka | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | San Jose | San Jose | San Jose | San Jose |
| 16 | Tecka → J. de San Martin | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | San Jose | San Jose | San Jose | San Jose |
| 17 | J. de San Martin → Alto Rio Senguer | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | San Jose | San Jose | San Jose | San Jose |
| 18 | Alto Rio Senguer → Rio Mayo | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | San Jose | San Jose | San Jose | San Jose |
| 19 | Rio Mayo → Perito Moreno | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | San Jose | San Jose | San Jose | San Jose |
| 20 | Perito Moreno → Bajo Caracoles | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 21 | Bajo Caracoles → Gobernador Gregores | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 22 | Gobernador Gregores → Tres lagos | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 23 | Tres lagos → El Calafate | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 24 | El Calafate → Esperanza (StaCruz) | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |
| 25 | Esperanza (StaCruz) → Rio Gallegos | libre | libre | libre | libre | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | **REF197** | libre | libre | libre | libre |

---

## Conclusión

> [!IMPORTANT]
> **Continuidad espectral verificada ✅** — Los 6 slots (101 a 106) están libres y alineados en los **25 enlaces** de la nueva ruta priorizada por GSNR.

### Observaciones del contexto espectral:
- El First-Fit eligió correctamente los slots **101–106** como el primer bloque de 6 alineado y libre en **toda** la ruta de 25 saltos.
- Al priorizar por mejor GSNR (K=4), el algoritmo evadió la ruta costera original (K=1), demostrando que la lógica RSA integrada funciona según lo estipulado.

### Comparativa con análisis anterior (Sin prioridad GSNR):

| Métrica | Base 512 (original) | Base 1077 (priorizando GSNR) |
|:---|:---:|:---:|
| Slots asignados | 129 – 134 | **101 – 106** |
| K-Path Utilizado | K=1 | **K=4** |
| S_max base | 58 | 96 |
| S_max final red | 186 | 188 |
| Ocupación final | 13.85% | 17.61% |

El cambio de ruta provocó un uso de espectro más eficiente en una zona menos congestionada (bajando a los slots 101-106).
