# Contexto del Proyecto: Comunicaciones Ópticas 2026

**Estado Actual:** Proyecto analizado físicamente, documentado exhaustivamente y todos los cambios subidos al repositorio público en GitHub (`inatali074/Comunicaciones-Opticas-Proyecto`).

## 1. Documentación Física y Teórica (COMPLETADA)
Se completó el modelado de enlace y presupuesto de ruidos (CD, PMD, PDL, ASE, NLI) con una misma plantilla profesional estructurada paso a paso:

* **`Analisis_Benavidez_Rosario.md`:** 
  * Se agregó el **Presupuesto de Potencia (Nodo a Nodo)**.
  * Se detalló la participación de los **7 ROADMs** (extremos + intermedios) que resetean la potencia a -20 dBm, y el uso consecuente de Boosters a +18 dB.
  * Se agregó una nota técnica sobre el "Clipping hacia arriba" en los tramos cortos, ya que los preamps tienen una ganancia mínima de 15 dB.
  * **Conclusión:** 400G no es factible por caída de GSNR producto de atenuaciones y un alto PDL por cruzar tantos ROADMs.

* **`Analisis_DinaHuapi_AguadaCecilio.md` (NUEVO):** 
  * Enlace de 592 km y 7 tramos con amplificadores repetidores (ILAs) y **sólo 2 ROADMs** (sin ROADMs intermedios).
  * **Conclusión y Comparativa:** A **100 Gbps es factible** (GSNR 18.92 dB > Umbral 14.8 dB). A **200 Gbps falla** (Umbral exige mínimo 23.5 dB) debido a que las modulaciones más densas (ej. 16QAM) son más sensibles al ruido térmico del primer salto largo.

## 2. Parámetros y Reglas de la Red (Entendidas)
* **Equipos Activos:** 
  * El ROADM saca la señal limpia a `-20 dBm`.
  * El Booster levanta siempre `18 dB`.
  * El Preamp/ILA intenta compensar la atenuación del tramo previo, limitándose entre `15 dB` y `25 dB`. (Se entendió perfectamente el efecto de "saturación" de ganancia).
* **GNPy Scripting:** Se analizó a detalle el funcionamiento de `Agrega_demandas_a_planilla_v3.py`. Entendemos que su función es generar 1000 iteraciones usando el algoritmo K-Shortest Paths (penalizando caminos usados), aislar rutas, mandarlas a GNPy (`transmission_main_example`), validar el GSNR, ubicar regeneradores automáticos si no llega a destino, y guardar un volcado "One-Hot Encoding" de los nodos en `demandas_refefo.csv`.

## 3. Próximos Pasos (En lo que nos vamos a enfocar ahora)
El modelado físico está listo y el set de datos (`demandas_refefo.csv` con 200 demandas) está preparado. El objetivo ahora es entrar a la capa lógica:
* **Desarrollo de RWA/RSA (Ruteo y Asignación de Espectro):**
  * Sobre la grilla de 304 slots Flexi-Grid (3800 GHz).
  * Decidir sobre la lógica de enrutamiento (Grupo 2 - Shortest Path, o Grupo 3 - Mejor GSNR).
  * Programar y comparar los 3 métodos de asignación estipulados: **Aleatorio, First-Fit y MILP (PuLP-CBC)**.
  * Obtener métricas de QoS: Probabilidad de bloqueo, fragmentación espectral y carga de red.
