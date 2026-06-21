# Metodología y Memoria de Cálculos de Enlaces Ópticos

Este documento detalla exhaustivamente las fórmulas matemáticas, los parámetros extraídos de los *datasheets/JSON* y las asunciones técnicas aplicadas para la generación del Excel `calculos_enlaces.xlsx`, el cual evalúa las rutas más comprometidas ("Benavidez - Mendoza" y "Dina Huapi - Aguada Cecilio").

---

## 1. Presupuesto de Potencia

El presupuesto de potencia evalúa las pérdidas del enlace físico y dimensiona la necesidad de amplificadores.

**Cálculos y Fórmulas:**
*   $\text{Pérdida Total (dB)} = L_{total} \times \alpha_{dB}$
*   $\text{Cantidad de Spans} = \lceil \frac{L_{total}}{L_{span}} \rceil$

**Datos Exactos extraídos:**
*   **Sensibilidad del receptor ($P_{rx}$):** `-20 dBm` (corresponde a `target_pch_out_db` del ROADM en `equipament.json`).
*   **Potencia de transmisión ($P_{tx}$):** `1 dBm` (corresponde a `power_dbm` en el JSON).

**⚠️ Asunciones de Diseño:**
*   **Atenuación ($\alpha_{dB}$):** Se utilizó el valor exacto del datasheet de la fibra Corning SMF-28 Ultra: **$0.18 \text{ dB/km}$** a 1550 nm.
*   **Cantidad de Spans ($N_{spans}$):** En lugar de asumir tramos ciegos de 80 km, se calculó la cantidad exacta de *spans* contando los nodos reales (ciudades) definidos en la "Ruta" de la simulación. La longitud de span ($L_{span}$) usada para el promedio en cálculos no lineales es la longitud total dividida por los tramos reales ($L_{total} / N_{spans}$).

---

## 2. Dispersión Cromática (CD)

Calcula el ensanchamiento del pulso de luz por efectos de dispersión.

**Cálculos y Fórmulas:**
*   Coeficiente de Dispersión: 
    $$ D(\lambda) = \frac{S}{4} \left( \lambda - \frac{\lambda_{ZD}^4}{\lambda^3} \right) \left[ \frac{\text{ps}}{\text{nm} \cdot \text{km}} \right] $$
*   Dispersión Total Acumulada: 
    $$ CD_{total} = D(\lambda) \times L_{total} \left[ \frac{\text{ps}}{\text{nm}} \right] $$

**Datos Exactos extraídos:**
*   **Longitudes de onda extremas y central:** $\lambda \in \{1534.8, 1550.0, 1565.2\} \text{ nm}$.
*   **Pendiente ($S$):** $0.093 \text{ ps}/(\text{nm}^2 \cdot \text{km})$.
*   **Cero dispersión ($\lambda_{ZD}$):** $1304 \text{ nm}$.
*   **Límites del DSP (del JSON):** Tolerancia de $\le 12,000 \text{ ps/nm}$ para 400G (16QAM) y $\le 77,000 \text{ ps/nm}$ para 100G (QPSK).

**⚠️ Asunciones de Diseño:**
*   No se contempla la instalación de bobinas compensadoras de dispersión (DCF) a lo largo del enlace; se asume que toda la mitigación recae sobre el Procesamiento Digital de Señal (DSP) coherente de los transceptores.

---

## 3. Relación Señal a Ruido Óptica (OSNR) y GSNR

La calidad general de la señal analógica a lo largo de su viaje.

**Cálculos y Metodología:**
*   Para esta sección **no se realizaron asunciones ni aproximaciones analíticas**. 
*   **Datos Exactos:** Los valores numéricos finales de `OSNR_ASE_dB` y el impacto no lineal `GSNR_NLI_dB` se inyectaron directamente leyendo las simulaciones provistas en el archivo `resultados_gsnr_demandas_base.csv` para garantizar exactitud contra el modelo computacional.

---

## 4. Dispersión por Modo de Polarización (PMD)

Evalúa el retardo entre las polarizaciones ortogonales de la luz.

**Cálculos y Fórmulas:**
*   Se calcula la suma cuadrática porque el PMD es un proceso estocástico:
    $$ PMD_{total} = \sqrt{\left(PMD_{coef\_fibra} \times \sqrt{L_{total}}\right)^2 + \left(N_{amps} \times PMD_{nodo}^2\right)} \text{ [ps]} $$

**Datos Exactos extraídos:**
*   **Coeficiente PMD Fibra:** **$0.04 \text{ ps}/\sqrt{\text{km}}$** (Sacado del PMD Link Design Value del datasheet `Corning-SMF28UOF.pdf`).
*   **PMD por Nodo (ROADM y OLA):** Se utilizó el valor exacto de **$3 \text{ ps}$** (`3e-12` s) extraído explícitamente de `equipament.json`.
*   **Cantidad de Nodos Físicos ($N_{nodos}$):** En lugar de estimar la cantidad de amplificadores por distancia, se extrajo la cantidad *exacta* contando las ciudades intermedias que atraviesa cada ruta específica según la columna "Ruta" del archivo `resultados_gsnr_demandas_base.csv`.

**⚠️ Asunciones de Diseño:**
*   Ninguna en esta sección. Todo el PMD fue acumulado matemáticamente utilizando estrictamente la información topológica real (nodos atravesados) y las especificaciones exactas del equipamiento.

---

## 5. Límite de Potencia por No Linealidades

Determina el umbral de potencia inyectada máximo antes de que la Auto Modulación de Fase (SPM) cause interferencia inaceptable.

**Cálculos y Fórmulas:**
*   Atenuación Lineal: 
    $$ \alpha_{lineal} = \frac{\alpha_{dB}}{4.343} \text{ [1/km]} $$
*   Longitud No Lineal Efectiva: 
    $$ L_{eff} = \frac{1 - e^{-\alpha_{lineal} \cdot L_{span}}}{\alpha_{lineal}} \text{ [km]} $$
*   Potencia Máxima (Límite no lineal 1 radián): 
    $$ P_{max\_lineal} = \frac{\lambda \cdot A_{eff}}{2 \pi \cdot n_2 \cdot L_{eff}} \text{ [Watts]} $$

**Datos Exactos extraídos:**
*   **Área Efectiva ($A_{eff}$):** $80 \mu m^2 = 80 \times 10^{-12} \text{ m}^2$ (Extraído del JSON y el Datasheet).
*   **Longitud de onda central ($\lambda$):** $1550 \text{ nm}$.

**⚠️ Asunciones de Diseño:**
*   **Índice de refracción no lineal ($n_2$):** Se utilizó el valor de **$2.21 \times 10^{-20} \text{ m}^2/\text{W}$** requerido específicamente para este cálculo de no linealidades.
*   **Criterio Analítico del Umbral:** Se fijó el límite igualando la ecuación a un desfasaje no lineal de $\Phi_{NL} \approx 1 \text{ radián}$, que es el umbral clásico de ingeniería en el cual las penalidades se vuelven inmanejables para constelaciones densas (16QAM).
