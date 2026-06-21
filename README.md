# Proyecto Integrador: Diseño y Actualización de Red Óptica a 400G

Este repositorio contiene el trabajo final correspondiente al diseño, actualización y análisis de la red óptica de Arsat, escalando las capacidades actuales hacia velocidades de hasta 400 Gbps utilizando equipamiento compatible con el estándar **Open-ROADM v5**.

## 🎯 Objetivos Principales del Proyecto

El proyecto se divide en las siguientes etapas fundamentales, abarcando desde la topología física hasta la asignación lógica de espectro (RSA/RWA):

### 1. Actualización de Infraestructura y Topología
* **Upgrade de Capacidades:** Reemplazo sistemático del tráfico existente por interfaces de mayor capacidad (1 Gbps → 100 Gbps; 10 Gbps → 200 Gbps; 40 Gbps → 300 Gbps; 100 Gbps → 400 Gbps).
* **Modelado de Red:** Actualización de la topología incorporando los nodos faltantes y definiendo el nuevo equipamiento activo y pasivo (`equipament_real_marcos_corregido.json` y `network_mashe.json`).
* **Consolidación de Demandas:** Procesamiento del tráfico base para generar el archivo estructurado `Demanda_Base - Tráfico base.csv`.

### 2. Análisis Analítico y Físico (Cálculos Teóricos)
Elección de los caminos más largos y comprometidos de la red para realizar cálculos rigurosos (a mano/planilla) que validen el diseño físico:
* **Presupuesto de Potencia:** Atenuaciones y ganancias en cascada.
* **Dispersión Cromática (CD):** Compensación en las 3 longitudes de onda más comprometidas (centro y extremos), considerando la pendiente de dispersión.
* **Cálculo de Ruido (OSNR):** Relación señal a ruido óptica de cada canal.
* **Impedimentos Adicionales:** Evaluación de los valores límites de PMD (Polarization Mode Dispersion) y de umbrales de potencia frente a efectos no lineales.

### 3. Simulación y Validación (Modelo GN)
* Análisis automatizado mediante *scripts* en Python (basado en lógica tipo GNPy) para rutas principales y de protección.
* Generación del reporte `resultados_gsnr_demandas_base.csv` reportando métricas finales como:
  * OSNR Térmico (ASE).
  * Ruido no lineal (GSNR NLI).
  * GSNR Total y factibilidad del enlace.

### 4. Ruteo y Asignación de Espectro (RWA / RSA)
Diseño sobre la grilla ITU-T Flexi-Grid con un ancho espectral total de 3800 GHz (304 slots de 12.5 GHz o 40 canales de 100 GHz de ancho de banda).
* **Métodos de Asignación:** Implementación y comparación de algoritmos de asignación de espectro:
  1. Aleatorio (Random).
  2. First-Fit.
  3. Mixed Integer Linear Programming (usando PuLP-CBC).
* **Ampliación de Tráfico:** Inyección de 200 demandas extras (provenientes de `demandas_refefo.csv`) para tensionar la red.
* **Análisis de Métricas de Calidad (QoS):**
  * Probabilidad de Bloqueo promedio y por enlace.
  * Fragmentación y contigüidad del espectro.
  * Variación de carga en la red (mínima y máxima ocupación de canales).
  * Salida de estado espectral (`ocupacion_slots_base.csv`).

## ⚙️ Estructura del Trabajo por Grupos
Para el análisis intensivo de las 200 demandas adicionales, la evaluación se bifurca dependiendo del criterio de enrutamiento:
* **Grupo 2:** Ruteo basado en los 5 caminos físicos más cortos (Shortest Path).
* **Grupo 3:** Ruteo analizando los 5 caminos con mejor desempeño óptico (Mejor GSNR).

---
*Documentación generada en base a las pautas de cátedra "Comunicaciones Ópticas 2026".*
