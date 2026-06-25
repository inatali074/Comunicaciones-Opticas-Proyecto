# Proyecto Integrador: Diseño y Actualización de Red Óptica a 400G

Este repositorio contiene el trabajo final correspondiente al diseño, actualización, análisis físico y asignación lógica de espectro de una red óptica DWDM basada en el footprint de ARSAT, escalando las capacidades hasta 400 Gbps utilizando equipamiento compatible con el estándar **Open-ROADM**.

---

## 📂 Estructura del Proyecto

El proyecto está modularizado en diferentes áreas críticas de análisis, reflejadas en la siguiente estructura de directorios:

### 1. Directorio Raíz
Contiene los archivos principales de ejecución global y datos base:
*   `calc_rutas_gsnr.py`: Script principal de estimación analítica. Calcula el desempeño físico (OSNR y GSNR NLI span-by-span) de las rutas, determinando la factibilidad de la señal puramente de forma analítica (sin llamar a GNPy).
*   `Demanda_Base - Tráfico base.csv`: Matriz de tráfico base con las 512 demandas originales.
*   `resultados_gsnr_demandas_base.csv`: Salida generada por el cálculo analítico.

### 2. `Excel_detallado/` - Análisis Teórico y Físico Detallado
Estudios analíticos y planillas de cálculo de performance física:
*   **Planillas de Enlaces:** `Excel_Calc_Detallado.xlsx` con los cálculos físicos detallados de los enlaces analizados.
*   **Ancho de Banda:** Carpeta `BW/` con el análisis y documentación del cálculo de ancho de banda (`calculo_ancho_banda.md`).

### 3. `Regeneracion/` - Módulo de Regeneración de Señal Óptica (OEO)
Algoritmo dinámico para salvaguardar enlaces no factibles:
*   `Regenerador.py`: Emplea un algoritmo "Greedy" de retroceso que utiliza simulaciones iterativas de la API de GNPy para determinar el ROADM óptimo donde ubicar regeneradores 3R en caso de que la GSNR acumulada caiga por debajo del umbral del transceptor.
*   `Regen_bajada.py`: Script alternativo de regeneración que evalúa alternativas bajando la velocidad de transmisión.

### 4. `RSA/` - Ruteo y Asignación de Espectro (RWA/RSA)
Resolución del problema de asignación espectral sobre grilla flexible (Flexi-Grid, 304 slots):
*   Modularizado en dos escenarios: Tráfico **base** (512 demandas) y tráfico extra de ampliación **REFEFO** (200 demandas adicionales).
*   Se comparan tres enfoques algorítmicos (First-Fit, Aleatorio y MILP con PuLP-CBC) incluyendo versiones mejoradas `_V2` para optimización de espectro.
*   Contiene el reporte general (`analisis_pablo_punto5.md`) y el script de tráfico dinámico (`generador_demandas_refefo.py`) adaptado con rutas portables.

### 5. `Analisis_Nodo_Cordoba/` - Análisis del Nodo Córdoba
Estudio integral del comportamiento físico y lógico del Nodo Córdoba:
*   Contiene scripts de graficación (`graficos_nodo_cordoba.py`), esquemas lógicos (`esquema_cordoba.dot`, `esquema_logico_cordoba.png`) y análisis detallado de la ocupación espectral y tráfico de la zona norte.

### 6. `Consigna/` e `Equipos/`
Archivos estáticos de configuración y referencias técnicas:
*   `Consigna/`: Json topológicos (`network_mashe.json`), diccionarios de equipos calibrados (`equipament_real_marcos_corregido.json`) y pdfs originarios de la cátedra.
*   `Equipos/`: Hojas de datos (Datasheets) de los componentes de hardware reales que modelan la simulación (Fibra SMF-28, Plataforma ROADM D7000, Transceptores Juniper 400G).

---

## 🚀 Cómo utilizar el repositorio

Todos los scripts de Python han sido reestructurados para utilizar **rutas relativas portables** (`os.path`). Esto significa que puedes clonar el repositorio en cualquier máquina y los scripts localizarán automáticamente los archivos JSON y CSV dependientes sin necesidad de intervenir el código.

**Requisitos Previos:**
* Python 3.12+ (Se recomienda usar entornos virtuales).
* Librerías genéricas: `pandas`, `numpy`, `networkx`, `pulp` (para el módulo RSA MILP).
* Para el script `Regenerador.py`, se requiere el entorno virtual local configurado con la dependencia específica `oopt-gnpy-libyang`.

---
*Desarrollado en el marco del Proyecto Integrador - Comunicaciones Ópticas 2026.*
