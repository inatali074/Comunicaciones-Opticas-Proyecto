# Análisis Integral del Nodo Central: Córdoba

Este documento detalla el análisis avanzado del nodo **Córdoba**, el punto de mayor criticidad y concentración de tráfico de toda la red óptica argentina. El análisis abarca la eficiencia en la asignación del espectro entre distintos algoritmos, el volumen de datos procesados (Throughput), el impacto dinámico de inyectar el tráfico del plan REFEFO y las implicaciones físicas de su hardware.

![Esquema Lógico de Ruteo en Córdoba](/home/nacho/Escritorio/Comunicaciones Opticas/trabajo final/Main/TpOpticas/Analisis_Nodo_Cordoba/esquema_logico_cordoba.png)

---

## 1. Comparativa de Algoritmos de Asignación (Tráfico Base)

Para demostrar por qué el algoritmo heurístico **First-Fit** es la elección óptima para la red, analizamos la ocupación del espectro (304 slots de 12.5 GHz) en **todos los enlaces físicos** conectados a Córdoba bajo tres estrategias de enrutamiento y asignación (RSA), inyectando las 512 demandas del Tráfico Base.

| Enlace Físico (ROADM) | Slots Usados | Slot Max (First-Fit) | Slot Max (Aleatorio) | Slot Max (MILP 60s) |
| :--- | :---: | :---: | :---: | :---: |
| **Córdoba ↔ Corralito** | 76 | **78** | 297 | 136 |
| **Córdoba ↔ Manfredi** | 64 | **96** | 297 | 120 |
| **Córdoba ↔ Jesús María** | 36 | **36** | 292 | 120 |
| **Córdoba ↔ La Falda** | 36 | **36** | 267 | 116 |
| **Córdoba ↔ Arroyito** | 28 | **36** | 240 | 136 |
| **Córdoba ↔ Serrezuela** | 20 | **20** | 300 | 20 |
| **Córdoba ↔ La Rioja** | 12 | **12** | 298 | 120 |
| **Córdoba ↔ V. Mercedes** | 4 | **4** | 227 | 4 |
| **Córdoba ↔ Patquía** | 4 | **4** | 240 | 4 |

**Conclusión Algorítmica:** First-Fit agrupa densamente los canales ópticos, logrando una fragmentación casi nula. El método *Aleatorio* inutiliza la fibra al dejar múltiples huecos, y el algoritmo *MILP* arroja asignaciones subóptimas altamente separadas al ser truncado por el límite de tiempo.

---

## 2. Impacto de Carga Masiva: Tráfico Base vs. REFEFO

Evaluamos cómo reacciona el espectro de Córdoba al sumar las 200 demandas de larga distancia del plan **REFEFO**. Para este escenario direccional, se muestra la carga máxima de los enlaces en el sentido más exigido.

| Enlace Físico (ROADM) | Slots Usados (Solo Base) | Slots Usados (Base + REFEFO) | Incremento de Carga | Slot Máx (REFEFO) |
| :--- | :---: | :---: | :---: | :---: |
| **Córdoba ↔ Corralito** | 76 | **152** | +100% | **176** |
| **Córdoba ↔ Arroyito** | 28 | **140** | +400% | **176** |
| **Córdoba ↔ Manfredi** | 64 | **110** | +71% | **188** |
| **Córdoba ↔ Jesús María** | 36 | **78** | +116% | **188** |
| **Córdoba ↔ La Falda** | 36 | **60** | +66% | **144** |
| **Córdoba ↔ Serrezuela** | 20 | **20** | 0% | **20** |
| **Córdoba ↔ La Rioja** | 12 | **12** | 0% | **12** |
| **Córdoba ↔ Patquía** | 4 | **10** | +150% | **106** |
| **Córdoba ↔ V. Mercedes** | 4 | **4** | 0% | **4** |

### Perfil de Tráfico: El Cuello de Botella "Express"
*   **En el escenario Base (58 canales totales):** 55 canales nacían o morían en Córdoba y **solo 3 canales** utilizaban el nodo como paso (*Express Bypass*).
*   **En el escenario REFEFO (113 canales totales):** El tráfico local se mantuvo, pero el tráfico de paso **explotó a 55 canales** (*Express Bypass*).

![Gráfico de Ocupación Espectral](/home/nacho/Escritorio/Comunicaciones Opticas/trabajo final/Main/TpOpticas/Analisis_Nodo_Cordoba/grafico_ocupacion.png)

---

## 3. Volumen de Tráfico y Throughput Físico (Tbps)

Evaluamos la cantidad de datos brutos (Throughput en Terabits por segundo - Tbps) que el hardware de Córdoba debe procesar, cruzando las capacidades de los canales (100G, 200G, 300G, 400G) asignados por First-Fit.

| Escenario | Tráfico Local (Add/Drop) | Tráfico de Paso (Express/Bypass) | **Throughput Total del Nodo** |
| :--- | :---: | :---: | :---: |
| **Solo Base** | 9.80 Tbps (55 demandas) | 1.00 Tbps (3 demandas) | **10.80 Tbps** |
| **Base + REFEFO** | 11.00 Tbps (58 demandas) | 13.90 Tbps (55 demandas) | **24.90 Tbps** |

**Conclusión Operativa y CAPEX:** 
*   **Saturación del WSS:** Al inyectar el plan REFEFO, el núcleo de conmutación óptica de Córdoba debe tener capacidad para enrutar casi **25 Tbps** simultáneos. El tráfico Express se multiplicó por casi 14x, demostrando empíricamente que el algoritmo convirtió a Córdoba en la rotonda principal del país.
*   **Inversión en Transceptores:** Los 11.00 Tbps de tráfico "Local" exigen que Córdoba tenga instalados físicamente transceptores (TRX) equivalentes a 28 módulos de 400 Gbps, representando una fuerte inversión en hardware (CAPEX) exclusiva para esta ciudad.

---

## 4. Impacto Físico y Penalidades del Hardware (Módulo `Bocco_punto3`)

De la extracción topológica (`network_mashe.json`), se constató que el equipo **`roadm Cordoba` es un nodo masivo de Grado 8 (Degree 8)**.

*   **El Costo del Bypass:** Las 55 portadoras ópticas que cruzan Córdoba "de largo" en REFEFO sufren:
    1.  Inserción de un **Pre-Amplificador EDFA** de entrada (Figura de Ruido ~5.5 dB).
    2.  Pérdida pasiva masiva (15 a 20 dB) al cruzar el Wavelength Selective Switch 1x9.
    3.  Inserción de un **Booster EDFA** de salida.

---

## 5. Calidad de Transmisión (QoT) según Flujo en Córdoba

A continuación se expone el desglose analítico completo de las conexiones del Tráfico Base (`resultados_gsnr_demandas_base_regenerado.csv`), detallando la distancia óptica, atenuación y necesidad de Regeneración OEO (3R).

### A. Tráfico que NACE en Córdoba (Salida)

| Origen | Destino | Distancia (km) | GSNR Final (dB) | Factible Directo | Req. Regen. 3R |
| :--- | :--- | :---: | :---: | :---: | :---: |
| Cordoba | Arroyito | 146.0 | 28.32 | SI | NO |
| Cordoba | San Francisco | 246.0 | 25.10 | SI | NO |
| Cordoba | Rafaela | 333.0 | 23.72 | SI | NO |
| Cordoba | V. Mercedes | 452.0 | 21.70 | SI | NO |
| Cordoba | Corralito | 85.0 | 28.56 | SI | NO |
| Cordoba | Hernando | 180.0 | 25.20 | SI | NO |
| Cordoba | Chucul | 268.0 | 23.61 | SI | NO |
| Cordoba | San Luis | 539.0 | 20.94 | NO | SI |
| Cordoba | Santa Rosa | 734.0 | 19.56 | NO | SI |
| Cordoba | Mendoza | 844.0 | 18.61 | NO | SI |

*(Nota: Filas redundantes con el mismo origen/destino/GSNR agrupadas para legibilidad).*

### B. Tráfico que MUERE en Córdoba (Entrada)

| Origen | Destino | Distancia (km) | GSNR Final (dB) | Factible Directo | Req. Regen. 3R |
| :--- | :--- | :---: | :---: | :---: | :---: |
| Villa Tulumaya | Cordoba | 813.0 | 21.21 | NO | SI |
| Media Agua | Cordoba | 713.0 | 22.25 | SI | NO |
| San Juan | Cordoba | 621.0 | 22.89 | SI | NO |
| Serrezuela | Cordoba | 230.0 | 26.05 | SI | NO |
| La Falda | Cordoba | 85.0 | 28.96 | SI | NO |
| Concepcion | Cordoba | 767.7 | 9.81 | NO | SI |
| Catamarca | Cordoba | 609.9 | 9.94 | NO | SI |
| La Rioja | Cordoba | 424.5 | 10.06 | NO | SI |
| Patquia | Cordoba | 374.1 | 15.07 | NO | SI |
| Tucuman | Cordoba | 731.0 | 20.93 | NO | SI |
| Santiago del Estero | Cordoba | 538.0 | 22.45 | SI | NO |
| Frias | Cordoba | 366.0 | 24.34 | SI | NO |
| Dean Funes | Cordoba | 139.0 | 27.00 | SI | NO |
| Jesus Maria | Cordoba | 54.0 | 30.54 | SI | NO |
| Cañada de Gomez | Cordoba | 413.0 | 21.03 | NO | SI |
| Leones | Cordoba | 305.0 | 22.70 | SI | NO |
| Villa Maria | Cordoba | 195.0 | 24.33 | SI | NO |
| Manfredi | Cordoba | 100.0 | 26.85 | SI | NO |
| Manfredi | Cordoba | 90.0 | 28.06 | SI | NO |
| Rosario | Cordoba | 503.0 | 20.32 | NO | SI |
| Benavidez | Cordoba | 778.0 | 18.67 | NO | SI |

### C. Tráfico de PASO por Córdoba (Express/Bypass)

Para el caso extremo de tráfico Express (ruta inicial calculada: `Benavidez ↔ Mendoza` de 1,622 km a 400G), la penalidad del ROADM de Córdoba genera un efecto de desviación en la red:

| Origen | Destino | Dist. Total (km) | GSNR Llegada a Córdoba (dB) | GSNR Salida de Córdoba (dB) | GSNR Llegada a Destino (dB) | Req. Regen. 3R |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Benavidez | Mendoza | 1622.0 | 18.67 | 18.29 | 15.65 | SI |
| Benavidez | Mendoza | 1622.0 | 18.67 | 18.29 | 15.65 | SI |

*(La caída de 18.67 dB a 18.29 dB se produce internamente solo por cruzar el ROADM de Grado 8 de Córdoba y el primer salto de fibra subsecuente).*

**El efecto evasivo de la Regeneración:**
Al ser procesada esta ruta por el script `Regenerador.py`, la degradación óptica es tan severa al cruzar Córdoba que el sistema **descarta** esta ruta en favor de una vía alternativa sur (Ruta Regenerada: `Benavidez ➝ Lujan ➝ Rufino ➝ Pehuajo ➝ Mendoza`). 

**Conclusión Operativa de Diseño:** Córdoba **aloja 0 (cero) regeneradores** ópticos en todo el análisis del Tráfico Base. Su penalidad física por inserción (Degree 8) es tan alta que el plano de control y el algoritmo de regeneración prefieren redirigir y regenerar las señales ultra-largas por caminos físicamente más marginales en lugar de inyectarlas al centro del país.
