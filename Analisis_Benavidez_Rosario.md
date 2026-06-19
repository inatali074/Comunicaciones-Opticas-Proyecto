# Análisis 400G — Benavídez → Rosario (351 km)
## Ruta Norte (vía Zárate)

---

## 1. Descripción del enlace

| Parámetro | Valor | Fuente |
|-----------|-------|--------|
| Ruta | Benavídez → Zárate → San Pedro → San Nicolás → Rosario | `Demanda_Base - Tráfico base.csv` (Ruta Norte) |
| Longitud total | 351 km | `network_mashe.json` (suma de spans) |
| Velocidad | 400 Gbps | `Demanda_Base - Tráfico base.csv` |
| Modulación | DP-16QAM | `equipament_real_marcos_corregido.json`, modo `400 Gbit/s, DP-16QAM` |
| Baud rate | 63.1 Gbaud = 63.1×10⁹ Hz | `equipament_real_marcos_corregido.json` |
| OSNR requerido (modo 400G) | 25,0 dB | `equipament_real_marcos_corregido.json` |
| tx_osnr del transceiver | 38,0 dB | `equipament_real_marcos_corregido.json` |
| Margen del sistema | 2 dB | `equipament_real_marcos_corregido.json` |
| GSNR del CSV | 22,84 dB | Salida del script `calc_rutas_gsnr.py` |

La topología real tiene nodos intermedios (Campana y Baradero) para completar la ruta Norte, dividiendo el enlace en 6 fibras:

```
[Tx] → R.Benavídez → B(18dB) → F.80km → P(16.5dB) → R.Campana
                                                       ↓
      R.Zárate ← P(15dB) ← F.13km ← B(18dB) ← [Campana]
         ↓
      B(18dB) → F.67km → P(15dB) → R.Baradero
                                      ↓
      R.San Pedro ← P(15dB) ← F.34km ← B(18dB) ← [Baradero]
         ↓
      B(18dB) → F.76km → P(15.7dB) → R.San Nicolás
                                         ↓
      [Rx] ← R.Rosario ← P(16.7dB) ← F.81km ← B(18dB) ← [S.Nicolás]
```

*(R = ROADM, B = Booster, P = Preamp, F = Fibra)*

### Parámetros de cada elemento de red (extraídos de `network_mashe.json` y `calc_rutas_gsnr.py`)

| Elemento | Tipo | Parámetro | Valor |
|----------|------|-----------|-------|
| Fibra B. → Campana | Fiber SSMF | Longitud / Atenuación | 80.0 km / 0.2 dB/km |
| Fibra Campana → Zárate | Fiber SSMF | Longitud / Atenuación | 13.0 km / 0.2 dB/km |
| Fibra Zárate → Baradero | Fiber SSMF | Longitud / Atenuación | 67.0 km / 0.2 dB/km |
| Fibra Baradero → San Pedro | Fiber SSMF | Longitud / Atenuación | 34.0 km / 0.2 dB/km |
| Fibra San Pedro → S. Nicolás | Fiber SSMF | Longitud / Atenuación | 76.0 km / 0.2 dB/km |
| Fibra S. Nicolás → Rosario | Fiber SSMF | Longitud / Atenuación | 81.0 km / 0.2 dB/km |
| Booster (todos los nodos) | Edfa OLA2525 | Ganancia forzada en script| 18.0 dB |
| Preamp Campana | Edfa OLA2525 | Ganancia | 16.5 dB |
| Preamp Zárate | Edfa OLA2525 | Ganancia (clipping min) | 15.0 dB |
| Preamp Baradero | Edfa OLA2525 | Ganancia (clipping min) | 15.0 dB |
| Preamp San Pedro | Edfa OLA2525 | Ganancia (clipping min) | 15.0 dB |
| Preamp San Nicolás | Edfa OLA2525 | Ganancia | 15.7 dB |
| Preamp Rosario | Edfa OLA2525 | Ganancia | 16.7 dB |

### Parámetros de fibra SSMF (extraídos de `equipament_real_marcos_corregido.json`)

| Parámetro | Valor en JSON | Conversión | Campo |
|-----------|--------------|------------|-------|
| Dispersión | 1.8×10⁻⁵ s/m² | **18.0 ps/(nm·km)** | `dispersion` |
| Área efectiva | 8.0×10⁻¹¹ m² | **80 µm²** | `effective_area` |
| Coef. PMD | 4.0×10⁻¹⁷ s/√m | **0.00126 ps/√km** | `pmd_coef` |

### Parámetros de EDFA OLA2525

| Parámetro | Valor | Campo / Script |
|-----------|-------|-------|
| NF | 5.5 dB | Fijo en el script `calc_rutas_gsnr.py` |
| PDL | 0.7 dB | `pdl` (JSON) |
| PMD | 3 ps | `pmd` (JSON) |

### Parámetros de ROADM

| Parámetro | Valor | Campo |
|-----------|-------|-------|
| Potencia objetivo por canal | −20 dBm | `target_pch_out_db` |
| PMD del ROADM | 3 ps | `pmd` (JSON) |
| PDL del ROADM | 1.5 dB | `pdl` (JSON) |

---

## 2. Presupuesto de Potencia

### Ecuación

$$
\text{Pérdida}_{fibra} = \alpha \cdot L + L_{conectores}
$$

$$
P_{salida} = P_{entrada} - \text{Pérdida}_{fibra} + G_{EDFA}
$$

El ROADM resetea la potencia a `target_pch_out_db = −20 dBm` según la lógica implementada en `calc_rutas_gsnr.py`.

### Valores usados

| Variable | Valor | Fuente |
|----------|-------|--------|
| P inicial (ROADM origen) | −20 dBm | `target_pch_out_db` |
| α (todos los spans) | 0.2 dB/km | `network_mashe.json` |
| L conectores totales | 0.5 dB / span | Hardcodeado en `calc_rutas_gsnr.py` |
| G booster (todos) | 18.0 dB | Script fuerza 18 dB para boosters |
| G preamp | Variable (15 a 25 dB) | Script compensa pérdida del span previo |

### Resultados

| ROADM | P salida ROADM (hacia Booster) | P inyectada a la Fibra |
|-------|-----------------|------|
| Todos los ROADMs | −20.00 dBm | −2.00 dBm |

---

## 3. OSNR (Optical Signal-to-Noise Ratio)

### Ecuación — OSNR de un amplificador individual

$$
OSNR_i \text{ [dB]} = P_{in} \text{ [dBm]} - NF \text{ [dB]} - 10 \cdot \log_{10}(h \cdot \nu \cdot B_{ref} \cdot 10^3)
$$

Constante ASE del script:
$$
10 \cdot \log_{10}(h \cdot \nu \cdot 12.5\times10^9 \cdot 10^3) = -57.95 \text{ dBm}
$$

Por lo tanto (con NF = 5.5 dB constante del script): $OSNR_i = P_{in} + 52.45$

### Cálculo de P_in en cada salto y OSNR_i

| EDFA | P_in (dBm) | OSNR_i (dB) |
|------|-----------|-------------|
| 6x Boosters (todos) | −20.00 | **32.45** |
| Preamp Campana | −18.50 | **33.95** |
| Preamp Zárate | −5.10 | **47.35** |
| Preamp Baradero | −15.90 | **36.55** |
| Preamp San Pedro | −9.30 | **43.15** |
| Preamp San Nicolás | −17.70 | **34.75** |
| Preamp Rosario | −18.70 | **33.75** |

### Ecuación — OSNR acumulado de la red

$$
OSNR_{red} = -10 \cdot \log_{10}\left( \sum 10^{-OSNR_i/10} \right) = \mathbf{23.13} \text{ dB}
$$

### OSNR total combinando transceiver

$$
OSNR_{total} = -10 \cdot \log_{10}\left(10^{-38.0/10} + 10^{-23.13/10}\right) = \mathbf{23.00} \text{ dB}
$$

---

## 4. GSNR (Generalized Signal-to-Noise Ratio)

El script provee una formulación de GSNR sumando el ruido ASE y el ruido no lineal NLI.

### Ecuación

$$
\frac{1}{GSNR} = \frac{1}{OSNR_{ASE}} + \frac{1}{GSNR_{NLI}}
$$

### Resultados de `calc_rutas_gsnr.py`

| Variable | Valor |
|----------|-------|
| OSNR ASE | 23.13 dB |
| GSNR NLI | 37.27 dB |
| GSNR Total (Incluyendo TX OSNR 38dB) | **22.84 dB** |

La penalidad NLI reduce el OSNR ASE de 23.13 dB a 22.97 dB (sin Tx), finalizando en 22.84 dB al incluir el transmisor.

---

## 5. Dispersión Cromática (CD)

### Ecuación

$$
CD_{acum} = D_0 \cdot L_{total}
$$

### Valores usados y Resultado

| Variable | Valor | Fuente |
|----------|-------|--------|
| D₀ | 18.0 ps/(nm·km) | `equipament_real_marcos_corregido.json` |
| L total | 351.0 km | Suma de spans |

$$
CD_{acum} = 18.0 \times 351.0 = \mathbf{6318.0 \text{ ps/nm}}
$$

Este valor requerirá alta capacidad de compensación electrónica en el DSP (usualmente soportado por transceptores modernos 400G hasta 10.000 ps/nm).

---

## 6. PMD (Polarization Mode Dispersion)

### Ecuación

$$
PMD_{total} = \sqrt{\sum PMD_{fibra}^2 + \sum PMD_{ROADM}^2 + \sum PMD_{EDFA}^2}
$$

### Valores usados

| Elemento | PMD individual | Cantidad |
|----------|-------|--------|
| Fibra | 0.00126 ps/√km | 351 km |
| ROADM | 3.0 ps | 7 nodos |
| EDFA | 3.0 ps | 12 amplificadores (6 Boosters + 6 Preamps) |

$$
PMD_{fibra\_sq} = (0.00126)^2 \times 351 \approx 0.0005 \text{ ps}^2
$$
$$
PMD_{equipos\_sq} = (7 \times 3.0^2) + (12 \times 3.0^2) = 63 + 108 = 171 \text{ ps}^2
$$
$$
PMD_{total} = \sqrt{0.0005 + 171} = \mathbf{13.08 \text{ ps}}
$$

El transceptor `TQD017-TUNC-SO` en 400G soporta hasta 10 ps sin penalidad, y aplica una penalidad de **0.5 dB** para 20 ps de PMD. Se espera una penalidad menor a 0.2 dB.

---

## 7. PDL (Polarization Dependent Loss)

### Ecuación

$$
PDL_{total} \approx \sqrt{\sum PDL_i^2}
$$

### Valores usados y Resultado

| Elemento | PDL individual | Cantidad |
|----------|-------|--------|
| ROADM | 1.5 dB | 7 nodos |
| EDFA | 0.7 dB | 12 amplificadores |

$$
PDL_{total} = \sqrt{7 \times (1.5)^2 + 12 \times (0.7)^2} = \sqrt{15.75 + 5.88} = \mathbf{4.65 \text{ dB}}
$$

El transceptor en modo 400G estipula en su matriz de penalidades que un PDL de 4 dB penaliza el enlace con **2.5 dB** adicionales, lo cual agravaría significativamente el desempeño.

---

## 8. ¿Se puede hacer el enlace a 400G?

### Criterio de factibilidad principal

$$
GSNR_{total} \geq OSNR_{req} + M_{sistema}
$$

| Variable | Valor |
|----------|-------|
| GSNR total | **22.84 dB** |
| OSNR requerido 400G | 25.0 dB |
| Margen del sistema | 2.0 dB |
| Umbral mínimo | 27.0 dB |

$$
22.84 \not\geq 27.0 \quad \Rightarrow \quad \text{\textbf{Margen = -4.16 dB}} \quad \text{NO FACTIBLE}
$$

### Verificación de todos los parámetros

| Parámetro | Valor Calculado | Límite / Penalidad (Transceiver JSON) | Resultado |
|-----------|-------|--------|-----------|
| GSNR Total | 22.84 dB | ≥ 27.0 dB | ❌ Margen negativo (-4.16 dB) |
| Dispersión Cromática | 6318.0 ps/nm | 12000 ps/nm (Penaliza 0.5 dB) | ✓ Operativo (0 dB penalidad extra) |
| PMD acumulada | 13.08 ps | 20 ps (Penaliza 0.5 dB) | ⚠️ Penalidad muy leve (~0.15 dB) |
| PDL acumulado | 4.65 dB | 4 dB (Penaliza 2.5 dB) | ❌ Exceso de PDL, alta penalidad |

### Conclusión

**No, el enlace Benavídez → Rosario (Ruta Norte, 351 km) NO es factible a 400G.**

La caída dramática del margen de OSNR se debe a la atenuación y figura de ruido (5.5 dB) acumulada en los 12 amplificadores del recorrido. Adicionalmente, el acumulado de PDL (4.65 dB) producto de atravesar 7 ROADMs introduce una severa penalidad extra que no está sumada en la fórmula analítica simplificada de GSNR del script, por lo que el rendimiento real sería incluso peor que los 22.84 dB calculados. 

Se requeriría operar este enlace a **200 Gbps** (cuyo umbral mínimo sin margen es mucho más tolerante) o instalar amplificación Raman para mitigar el alto ruido térmico inyectado por los preamplificadores.

---

## 9. Presupuesto de Potencia (Nodo a Nodo)

La potencia de salida objetivo (`target_pch_out`) configurada en todos los ROADMs es de **-20 dBm**. Para salir de cada ROADM hacia la fibra, el script fuerza empíricamente una ganancia de **18 dB** en los amplificadores Booster, inyectando de forma constante **-2 dBm** a cada tramo de fibra de la Ruta Norte.
Al llegar al siguiente nodo, los preamplificadores intentan compensar la atenuación del tramo anterior, pero están limitados físicamente a un rango de ganancia de entre 15 dB (mínimo) y 25 dB (máximo).

| Origen | Ganancia Booster | Atenuación Tramo (Fibra) | Destino (Siguiente Nodo) | $P_{in}$ al Preamp dest. | Ganancia Preamp | $P_{out}$ del Preamp |
|--------|------------------|--------------------------|--------------------------|--------------------------|-----------------|----------------------|
| ROADM Benavídez | 18.00 dB | -16.50 dB (80 km) | ROADM Campana | -18.50 dBm | 16.50 dB | -2.00 dBm |
| ROADM Campana | 18.00 dB | -3.10 dB (13 km) | ROADM Zárate | -5.10 dBm | 15.00 dB (mín) | +9.90 dBm |
| ROADM Zárate | 18.00 dB | -13.90 dB (67 km) | ROADM Baradero | -15.90 dBm | 15.00 dB (mín) | -0.90 dBm |
| ROADM Baradero | 18.00 dB | -7.30 dB (34 km) | ROADM San Pedro | -9.30 dBm | 15.00 dB (mín) | +5.70 dBm |
| ROADM San Pedro | 18.00 dB | -15.70 dB (76 km) | ROADM San Nicolás| -17.70 dBm | 15.70 dB | -2.00 dBm |
| ROADM S. Nicolás| 18.00 dB | -16.70 dB (81 km) | ROADM Rosario | -18.70 dBm | 16.70 dB | -2.00 dBm |

*Nota:* Después del $P_{out}$ del Preamp de destino, la señal ingresa al ROADM de esa ciudad, donde el hardware interno (WSS) se encarga de atenuar y ecualizar el canal automáticamente para llevarlo de vuelta al target exacto de **-20 dBm**. Una vez en -20 dBm, se inyecta al siguiente Booster repitiendo el ciclo.

**Nota técnica de Clipping Mínimo:** Se observa que en tramos cortos como Campana → Zárate (13 km) o Baradero → San Pedro (34 km) la fibra pierde muy poca potencia. El Preamp de destino recibe la señal con potencias relativamente altas (ej. -5.10 dBm en Zárate). Como el límite mínimo de diseño del EDFA en el script es de 15 dB de ganancia, el amplificador inevitablemente "clipea" su ganancia hacia arriba y entrega una potencia muy alta (+9.90 dBm), delegando la carga de atenuar todo ese exceso al WSS del ROADM para volver a los -20 dBm objetivos.
