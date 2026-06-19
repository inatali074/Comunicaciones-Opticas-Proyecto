# Contexto del Proyecto: Comunicaciones Ópticas 2026

**Estado Actual:** Proyecto analizado, documentado y subido a GitHub (repositorio público `inatali074/Comunicaciones-Opticas-Proyecto`). 

## 1. Archivos y Documentación Generada
* **`Analisis_Benavidez_Rosario.md`**: Se realizó un análisis profundo de viabilidad del enlace Benavídez → Rosario siguiendo la "Ruta Norte" (351 km, 6 tramos). Se adaptó estrictamente al formato solicitado por la cátedra (basado en el archivo de referencia de Santa Fe → Sunchales). El análisis incluye:
  * Presupuesto de potencia y uso de ROADMs (-20 dBm target).
  * Ecuaciones de OSNR (Ruido ASE de los 12 EDFAs).
  * Ecuaciones de GSNR (considerando efectos NLI).
  * Cálculo y verificación de Dispersión Cromática (CD), PMD y PDL.
  * **Conclusión:** El enlace a 400G (DP-16QAM) es **no factible** con los parámetros actuales (GSNR = 22.84 dB vs Umbral = 27.0 dB) debido a las penalizaciones por ruido térmico en los 6 tramos y el exceso de PDL al cruzar 7 ROADMs.
* **`README.md`**: Creado en base al archivo de consignas (`¿Qué hacer_ Opticas 2026.pdf`), estructura de forma profesional los objetivos del TP (upgrade a 400G, generación de topología corregida, modelado matemático de OSNR/GSNR y posterior análisis de RWA/RSA con los Grupos 2 y 3).
* **Git/GitHub**: Se inicializó el control de versiones, configurando el gestor de credenciales localmente para permitir subidas automáticas al repositorio `main` sin solicitar *Personal Access Tokens* interactivos. 

## 2. Parámetros Técnicos y Suposiciones Clave
* **Transceptor a 400G:** Requiere OSNR de 25.0 dB + 2 dB de margen de sistema (Umbral 27.0 dB).
* **Equipos Activos:** Boosters seteados empíricamente a 18 dB y Preamplificadores variables compensando la pérdida del tramo (mínimo 15 dB). Todos los EDFAs asumen NF=5.5 dB por limitación del script evaluador.
* **Fibra Óptica:** Atenuación de 0.2 dB/km + 0.5 dB adicionales por conectores. Coeficiente de dispersión 18.0 ps/(nm*km).
* **Capacidad Máxima Práctica:** Determinamos que bajo este modelo, la distancia máxima viable para alcanzar 27 dB de GSNR está en el orden de los **150 a 160 km** continuos sin regeneración.

## 3. Próximos Pasos (Pendientes)
El contexto queda listo para continuar con:
* Análisis RWA/RSA sobre las 200 demandas del archivo `demandas_refefo.csv`.
* Desarrollo de la lógica de asignación de espectro para el Grupo 2 (camino más corto) o Grupo 3 (mejor GSNR).
* Simulación de los métodos de asignación: Aleatorio, First-Fit y Mixed Integer Linear Programming (PuLP-CBC).
* Cálculo de métricas finales: probabilidad de bloqueo, fragmentación, y carga de la red.
