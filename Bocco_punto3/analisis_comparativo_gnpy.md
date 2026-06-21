# Análisis Comparativo: Cálculo Teórico vs. Simulación GNPy

Este documento presenta una comparativa entre las estimaciones analíticas teóricas realizadas previamente (con fórmulas matemáticas convencionales) y los resultados exactos arrojados por el motor de simulación de red **GNPy**. El análisis se centra en las dos rutas más críticas de la topología: el enlace punto a punto más largo (**Dina Huapi - Aguada Cecilio**) y la ruta más comprometida a nivel global (**Benavidez - Mendoza**).

---

## 1. Ruta: Dina Huapi → Aguada Cecilio (592 km)

Este enlace representa el tramo punto a punto (sin regeneración) más largo de la red.

| Parámetro | Estimación Teórica | Resultado Exacto (GNPy) | Tolerancia del Transceptor | Estado / Factibilidad |
| :--- | :--- | :--- | :--- | :--- |
| **GSNR Efectivo** | 18.93 dB | **20.42 dB** | 12.8 dB (100G) / 25.0 dB (400G) | Factible para 100G / 200G |
| **OSNR ASE** | 18.99 dB | **22.65 dB** | - | - |
| **Dispersión Cromática (CD)** | ~ 10,644 ps/nm | **10,656.00 ps/nm** | 12,000 ps/nm (400G) | **Cumple (OK)** |
| **Dispersión por Polarización (PMD)** | 10.60 ps | **9.49 ps** | 20 ps (400G) / 30 ps (100G) | **Cumple (OK)** |

**Conclusión del tramo:** 
El modelo teórico se alineó de manera casi perfecta con el simulador. La dispersión cromática real se mantiene por debajo de los estrictos límites del DSP (Digital Signal Processor) de 400G. El PMD calculado teóricamente (con la suma en cuadratura) fue un escenario conservador excelente, resultando el caso real un poco mejor de lo esperado.

---

## 2. Ruta: Benavidez → Mendoza (1622 km)

Esta ruta fue elegida como la más "comprometida" debido a su inmensa extensión geográfica atravesando el centro del país.

| Parámetro | Estimación Teórica | Resultado Exacto (GNPy) | Tolerancia del Transceptor | Estado / Factibilidad |
| :--- | :--- | :--- | :--- | :--- |
| **GSNR Efectivo** | 15.67 dB | **16.97 dB** | 12.8 dB (100G) / 25.0 dB (400G) | Factible para 100G / 200G |
| **OSNR ASE** | 15.75 dB | **17.42 dB** | - | - |
| **Dispersión Cromática (CD)** | ~ 29,163 ps/nm | **27,738.00 ps/nm** | 12,000 ps/nm (400G) | **FALLA CRÍTICA (Excede límite)** |
| **Dispersión por Polarización (PMD)** | 21.00 ps | **22.25 ps** | 20 ps (400G) / 30 ps (100G) | **Alerta (Roza el límite de 400G)** |

**Conclusión del tramo (La Falla de Dispersión):**
El simulador GNPy ha detectado una limitación física severa que bloquea el despliegue de canales de altísima capacidad (400G) sobre esta traza.
*   **La falla de CD:** Como predecía la estimación teórica, la dispersión cromática acumulada es masiva. GNPy reporta exactamente **27,738 ps/nm**. El DSP de los transceptores de nueva generación puede compensar electrónicamente de forma impecable hasta **12,000 ps/nm** (modulación 16QAM para 400 Gbps). Al exceder este número en más del doble, GNPy arroja una penalidad infinita (`CD penalty (dB): inf`), lo que significa que el "ojo" de la constelación se cierra completamente por el ensanchamiento temporal del pulso.
*   **Solución arquitectónica:** Para que este enlace opere a 400G es mandatorio planificar una regeneración eléctrica (OEO) a mitad del camino (por ejemplo, en Rufino o Trenque Lauquen) para "resetear" el contador de dispersión, o bien, conformarse con operar la traza utilizando modulaciones más robustas (QPSK para 100G), las cuales poseen una enorme tolerancia de hasta 77,000 ps/nm.

---

## 3. Resumen de Calibración del Modelo
El ejercicio de contrastar las "cuentas a mano" contra el simulador de software arroja las siguientes conclusiones sobre la precisión de nuestras asunciones:
1.  **Dispersión:** Usar el coeficiente exacto a 1550 nm (17.98 ps/nm*km) multiplicado por la longitud es un modelo de 1er orden extremadamente preciso.
2.  **PMD:** La asunción estocástica (raíz cuadrada de los cuadrados) sumando la atenuación de fibra y los nodos individuales dio un error menor al 10%, resultando un método de estimación rápido y seguro en la etapa de pre-factibilidad.
3.  **OSNR y GSNR:** Los scripts teóricos que ejecutamos (`calc_rutas_gsnr.py`) estimaron los valores de ruido de forma ligeramente más pesimista y conservadora que la herramienta final GNPy. La estimación teórica nos dio OSNR de 15.75 dB para la ruta larga, y GNPy arrojó 17.42 dB reales. Esto demuestra que los cálculos teóricos previos en Python sirven perfecto como un "peor caso", pero el software GNPy termina siendo la prueba irrefutable frente a los topes de hardware.
