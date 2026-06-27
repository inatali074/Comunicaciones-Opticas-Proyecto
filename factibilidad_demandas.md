# Reporte de Factibilidad Física de las 512 Demandas de la Red Óptica (Límite: Max 4 Regeneradores)

Este reporte presenta el análisis de factibilidad de transmisión para las **512 demandas de tráfico** en la red óptica nacional. El estudio se divide en tres fases incrementales de optimización física:
1. **Fase 1 (Base Directa):** Simulación directa de extremo a extremo sin regeneración óptica.
2. **Fase 2 (Regenerada):** Colocación de regeneradores 3R en nodos ROADM intermedios, limitada a un **máximo de 4 regeneradores** por demanda.
3. **Fase 3 (Reducción de Velocidad / Speed-down):** Ajuste de la tasa de transmisión (de 400G/200G a 300G/100G) en los enlaces críticos que no cumplen con los límites físicos o la restricción de equipamiento.

---

## 1. Resumen Ejecutivo

A continuación, se presenta la evolución de la factibilidad de la red a través de las tres fases del proyecto incorporando la restricción de **máximo 4 regeneradores**:

| Fase | Descripción de la Mitigación | Demandas Factibles | Demandas No Factibles | Tasa de Factibilidad | Estado de la Red |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Fase 1** | Transmisión base directa (extremo a extremo) | 434 | 78 | **84.77%** | Incompleto (78 caídas) |
| **Fase 2** | Asignación de Regeneradores 3R (máx. 4 por canal) | 502 | 10 | **98.05%** | Optimizado (10 caídas) |
| **Fase 3** | Reducción de velocidad en tramos y cuellos críticos | 512 | 0 | **100.00%** | **Totalmente Factible** |

> [!NOTE]
> Al finalizar las tres fases de optimización, el **100% de las demandas (512/512)** se encuentran operativas y físicamente viables, garantizando la conectividad de toda la topología nacional respetando el límite estricto de equipamiento regenerador.

---

## 2. Fase 1: Factibilidad Base (Directa)

En la simulación base directa, la señal viaja sin regeneración intermedia. De las 512 demandas, **434 son factibles (84.77%)** y **78 no son factibles (15.23%)** debido a que la relación señal a ruido generalizada (GSNR) cae por debajo del umbral de OSNR requerido por sus transceptores.

### Análisis Geográfico por Región (Fase 1)

*   **Región Sur (Tasa de Factibilidad: 94.78%):** Cuenta con 115 demandas, de las cuales 109 son factibles. La distancia promedio de los enlaces es la más baja de la red (**183.17 km**), con tramos cortos que minimizan la acumulación de ruido ASE y no linealidades.
*   **Región Norte (Tasa de Factibilidad: 89.72%):** Concentra la mayor cantidad de demandas (214), con 192 factibles de forma directa. La distancia promedio de enlace es de **311.94 km**, tolerando bien las transmisiones debido a una topología en malla con buenas calidades de fibra.
*   **Región Centro (Tasa de Factibilidad: 72.68%):** Presenta el peor desempeño directo. De 183 demandas, solo 133 son factibles. La distancia promedio es la más alta (**341.63 km**) y contiene los trayectos más largos del país, incluyendo el enlace crítico `Benavidez - Mendoza` con **1,622 km** de extensión, inviable para cualquier transmisión directa a alta velocidad.

---

## 3. Fase 2: Factibilidad con Regeneración Óptica 3R (Límite: Máx 4)

La regeneración 3R (Re-amplificación, Re-conformación y Re-sincronización) en los ROADMs intermedios permite limpiar la señal óptica del ruido acumulado, convirtiéndola momentáneamente al dominio eléctrico y re-transmitiéndola al dominio óptico. Esto "resetea" el presupuesto de ruido y permite cubrir distancias mucho mayores.

Al aplicar el algoritmo de asignación óptima de regeneradores con un límite estricto de **máximo 4 regeneradores**, **68 de las 78 demandas fallidas se volvieron factibles**, elevando la factibilidad al **98.05% (502 de 512)**. Las 10 demandas que no fueron factibles se dividen en tres categorías:

1.  **Cuellos de botella físicos (2 demandas en la Patagonia):**
    *   `Dina Huapi - Aguada Cecilio` (592 km) y `Piedra del Aguila - Bahia Blanca` (1,380 km, que transita por el mismo tramo anterior). No es posible usar regeneradores debido a la falta de ROADMs intermedios en dicho tramo.
2.  **Falsos negativos por bugs de software (6 demandas):**
    *   Casos de desajustes gramaticales de ciudades (ej. `San Miguel de Tucumán` vs `Tucuman`, `Saenz Peña` vs `Presidencia Roque Saenz Peña`, `V. Mercedes` vs `Villa Mercedes`) que impidieron su mapeo físico. Requieren menos de 4 regeneradores y se corrigen automáticamente en la Fase 3.
3.  **Exceso del límite de equipamiento (2 demandas de larga distancia):**
    *   `Benavidez - Mendoza` (1,622 km, requería originalmente 10 regeneradores a 400 Gbps).
    *   `Rosario - Resistencia` (911 km, requería originalmente 5 regeneradores a 400 Gbps).
    *   Ambos enlaces superaban el límite establecido de 4 regeneradores y fueron declarados no factibles en esta fase para obligar a una reducción de velocidad en la Fase 3.

---

## 4. Fase 3: Mitigación por Reducción de Velocidad (Speed-down)

Para resolver las 10 demandas no factibles de la Fase 2 bajo el límite de equipamiento, se implementó una lógica de reducción de velocidad (speed-down). Al bajar la velocidad, el formato de modulación es más robusto y el umbral de OSNR requerido disminuye sustancialmente, reduciendo la necesidad de regeneradores intermedios.

Las 10 demandas se resolvieron por completo en esta fase de la siguiente manera:
- Las **6 demandas** con problemas de nombres se normalizaron y resultaron factibles a su velocidad original de 200 Gbps utilizando $\le 4$ regeneradores.
- Las **4 demandas** restantes aplicaron reducción de velocidad para alcanzar la factibilidad:

| Canal Crítico | Distancia (km) | Velocidad Original | Velocidad Ajustada | Regeneradores en Estado Final | Margen de GSNR final |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Dina Huapi $\rightarrow$ Aguada Cecilio** | 592 km | 200 Gbps | 100 Gbps | **0** (Sin ROADMs intermedios) | $+8.18$ dB (GSNR: 19.98 dB / Umbral: 11.80 dB) |
| **Piedra del Aguila $\rightarrow$ Bahia Blanca** | 1,380 km | 200 Gbps | 100 Gbps | **0** (Sin ROADMs en tramo crítico) | $+4.91$ dB (GSNR: 16.71 dB / Umbral: 11.80 dB) |
| **Rosario $\rightarrow$ Resistencia** | 911 km | 400 Gbps | 100 Gbps | **0** (Desactiva regeneradores) | $+5.96$ dB (GSNR: 17.76 dB / Umbral: 11.80 dB) |
| **Benavidez $\rightarrow$ Mendoza** | 1,622 km | 400 Gbps | 100 Gbps | **0** (Desactiva regeneradores) | $+3.85$ dB (GSNR: 15.65 dB / Umbral: 11.80 dB) |

### Análisis de la Decisión de Ingeniería

La implementación del límite de un máximo de 4 regeneradores demuestra ser una **decisión de diseño óptima**:
- **Gran ahorro de equipamiento:** En la red original, la demanda `Benavidez - Mendoza` utilizaba 10 regeneradores y `Rosario - Resistencia` utilizaba 5. Al limitar el máximo a 4 y realizar la reducción a 100 Gbps directo, la cantidad combinada de regeneradores para estos dos enlaces cayó de **15 a 0** (un ahorro de 15 tarjetas de transceptores en los ROADMs).
- **Mínimo impacto de ancho de banda:** El 99.2% de los enlaces de la red mantuvieron intacta su velocidad de diseño. Solo 4 enlaces se redujeron de velocidad (dos de 200G a 100G, y dos de 400G a 100G), disminuyendo la capacidad agregada en un porcentaje insignificante a cambio de una reducción sustancial de costos en equipamiento (CAPEX) y consumo energético en ROADMs intermedios (OPEX).

---

## 5. Estadísticas de Velocidad y Regeneradores (Estado Final)

### Perfil de Velocidades Ajustadas de la Red

La distribución final de velocidades de transmisión queda estructurada de la siguiente manera:

| Velocidad de Canal | Cantidad de Demandas (Original) | Cantidad de Demandas (Ajustada) | Porcentaje de la Red |
| :--- | :---: | :---: | :---: |
| **400 Gbps** | 3 | 1 | 0.20% |
| **300 Gbps** | 43 | 43 | 8.40% |
| **200 Gbps** | 280 | 278 | 54.30% |
| **100 Gbps** | 186 | 190 | 37.11% |
| **Total** | **512** | **512** | **100.00%** |

### Distribución de Equipamiento (Nodos Regeneradores)

Bajo las nuevas restricciones de la red, se requiere instalar un total de **100 tarjetas regeneradoras** en toda la infraestructura nacional (comparado con las 115 requeridas sin la restricción). La distribución por demanda es la siguiente:

- **0 Regeneradores (Transmisión Directa):** 447 demandas (87.30%)
- **1 Regenerador:** 38 demandas (7.42%)
- **2 Regeneradores:** 20 demandas (3.91%)
- **3 Regeneradores:** 6 demandas (1.17%)
- **4 Regeneradores:** 1 demanda (0.20%)
- **Total:** **512 demandas (100 regeneradores en total)**

---

## 6. Gráficos y Visualizaciones

A continuación se presentan los gráficos estadísticos que ilustran el comportamiento físico del sistema:

### Gráfico 1: Evolución de Factibilidad de la Red
Este gráfico muestra cómo se resuelve la conectividad de la red agregando regeneradores y aplicando bajadas de velocidad específicas.
![Evolución de Factibilidad](./graficos/evolucion_factibilidad.png)

### Gráfico 2: Distribución de la Cantidad de Regeneradores
Muestra que el 86.91% de las demandas (445) no requiere regeneradores intermedios, y bajo la restricción impuesta, el caso máximo ahora requiere un máximo de 4.
![Distribución de Regeneradores](./graficos/distribucion_regeneradores.png)

### Gráfico 3: Comparación de Velocidades Originales vs. Ajustadas
Muestra que la red conserva casi la totalidad de su ancho de banda original, habiéndose reducido la velocidad en solo 4 canales.
![Velocidades Finales](./graficos/velocidades_finales.png)

### Gráfico 4: Relación Distancia vs. GSNR Final
En este gráfico de dispersión se visualiza la decaída de la GSNR física a medida que aumenta la distancia del enlace en kilómetros. 
- Los puntos azules (directos) se concentran en distancias menores a 600 km con GSNR altas.
- Los puntos verdes (con regeneración) cubren distancias de hasta 1,622 km, operando de manera estable gracias al reseteo de GSNR en cada nodo intermedio.
- Los puntos naranjas y amarillos representan los canales restringidos por la física del tramo `Dina Huapi - Aguada Cecilio` (100G) y por la restricción de cantidad de regeneradores (300G).
![Relación Distancia vs GSNR](./graficos/distancia_vs_gsnr.png)

---

## 7. Conclusiones y Recomendaciones de Ingeniería

1.  **Éxito de la Restricción de Regeneradores:** El límite de un máximo de 4 regeneradores redujo en un **13.0% la cantidad total de tarjetas regeneradoras** en la red (de 115 a 100) con un impacto despreciable en el rendimiento de datos. Se recomienda adoptar esta política de diseño.
2.  **Cuello de Botella Físico en la Patagonia:** El enlace `Dina Huapi - Aguada Cecilio` (592 km) sigue siendo la principal limitación física para el transporte de alta capacidad en el sur de la red. Si se desea elevar la velocidad de estas demandas a 200 Gbps en el futuro, se recomienda instalar un **amplificador intermedio activo (OLA - Optical Line Amplifier)** o un ROADM intermedio en dicha ruta para segmentar la fibra física y elevar la GSNR recibida.
3.  **Habilitación de Canales de Alta Capacidad (300G/400G):** Las demandas diseñadas a 300 Gbps y 400 Gbps resultaron factibles de forma directa en su gran mayoría debido a que se asignaron a rutas cortas y optimizadas. Esto demuestra que la red tiene la capacidad de soportar transmisiones de ultra alta velocidad en tramos metropolitanos sin necesidad de equipamiento de regeneración costoso.
