# Análisis 100G/200G — Dina Huapi → Aguada Cecilio (592 km)

---

## 1. Descripción del enlace

| Parámetro | Valor | Fuente |
|-----------|-------|--------|
| Ruta | Dina Huapi → Comallo → Ing. Jacobacci → Maquinchao → Los Menucos → Ministro Ramos Mexía → Nahuel Niyeu → Aguada Cecilio | `network_mashe.json` (Búsqueda por caminos más cortos) |
| Longitud total | 592.0 km | Suma de tramos |
| Velocidad | 100 Gbps y 200 Gbps | Requerimiento de análisis |
| GSNR Total de la línea | **18.92 dB** | Salida del script `calc_rutas_gsnr.py` |
| OSNR requerido (100G) | 12.8 dB | `equipament_real_marcos_corregido.json` |
| OSNR requerido (200G) | 21.5 dB | `equipament_real_marcos_corregido.json` |
| tx_osnr del transceiver | 38.0 dB | `equipament_real_marcos_corregido.json` |
| Margen del sistema | 2.0 dB | `equipament_real_marcos_corregido.json` |

El enlace está dividido en **7 tramos de fibra**, atravesando 6 nodos intermedios que actúan como estaciones repetidoras (ILA - In Line Amplifiers), más el nodo de transmisión (Booster) y el de recepción (Preamp).

```text
[Tx] → R.Dina Huapi → B(18dB) → F.107km → ILA(25.0dB) → [Comallo]
                                                             ↓
        [Maquinchao] ← ILA(18.6dB) ← F.77km ← ILA(22.8dB) ← F.95km
             ↓
        F.74km → ILA(17.9dB) → [Los Menucos] → F.96km → ILA(23.1dB) → [M. Ramos Mexía]
                                                                             ↓
        [Rx] ← R.Aguada Cecilio ← P(19.1dB) ← F.79km ← ILA(15.5dB) ← F.64km ← [Nahuel Niyeu]
```
*(R = ROADM, B = Booster, ILA = In-Line Amplifier, P = Preamp, F = Fibra)*

### Parámetros de cada elemento de red (extraídos de `network_mashe.json` y `calc_rutas_gsnr.py`)

| Elemento | Tipo | Parámetro | Valor |
|----------|------|-----------|-------|
| Fibra Dina Huapi → Comallo | Fiber SSMF | Longitud / Atenuación aprox | 107.0 km / 0.235 dB/km |
| Fibra Comallo → Ing. Jacobacci | Fiber SSMF | Longitud / Atenuación aprox | 95.0 km / 0.235 dB/km |
| Fibra Ing. Jacobacci → Maquinchao | Fiber SSMF | Longitud / Atenuación aprox | 77.0 km / 0.235 dB/km |
| Fibra Maquinchao → Los Menucos | Fiber SSMF | Longitud / Atenuación aprox | 74.0 km / 0.235 dB/km |
| Fibra Los Menucos → M. Ramos Mexía | Fiber SSMF | Longitud / Atenuación aprox | 96.0 km / 0.235 dB/km |
| Fibra M. Ramos Mexía → Nahuel Niyeu | Fiber SSMF | Longitud / Atenuación aprox | 64.0 km / 0.235 dB/km |
| Fibra Nahuel Niyeu → Aguada Cecilio | Fiber SSMF | Longitud / Atenuación aprox | 79.0 km / 0.235 dB/km |
| Booster Dina Huapi | Edfa OLA2525 | Ganancia forzada en script | 18.0 dB |
| ILA Comallo | Edfa OLA2525 | Ganancia (clipping max) | 25.0 dB |
| ILA Ing. Jacobacci | Edfa OLA2525 | Ganancia | 22.82 dB |
| ILA Maquinchao | Edfa OLA2525 | Ganancia | 18.59 dB |
| ILA Los Menucos | Edfa OLA2525 | Ganancia | 17.89 dB |
| ILA M. Ramos Mexía | Edfa OLA2525 | Ganancia | 23.06 dB |
| ILA Nahuel Niyeu | Edfa OLA2525 | Ganancia | 15.54 dB |
| Preamp Aguada Cecilio | Edfa OLA2525 | Ganancia | 19.06 dB |

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

## 2. Presupuesto de Potencia (Ecuación y Valores Base)

### Ecuación

$$
\text{Pérdida}_{fibra} = \alpha \cdot L + L_{conectores}
$$

$$
P_{salida} = P_{entrada} - \text{Pérdida}_{fibra} + G_{EDFA}
$$

El ROADM resetea la potencia a `target_pch_out_db = −20 dBm`.

### Valores usados

| Variable | Valor | Fuente |
|----------|-------|--------|
| P inicial (ROADM origen) | −20 dBm | `target_pch_out_db` |
| α (todos los spans) | ~0.235 dB/km | `network_mashe.json` |
| L conectores totales | 0.5 dB / span | Hardcodeado en `calc_rutas_gsnr.py` |
| G booster | 18.0 dB | Script fuerza 18 dB para boosters |
| G ILA/preamp | Variable (15 a 25 dB) | Script compensa pérdida del span previo |

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
| Booster Dina Huapi | −20.00 | **32.45** |
| ILA Comallo | −27.64 | **24.81** |
| ILA Ing. Jacobacci | −25.46 | **26.99** |
| ILA Maquinchao | −21.23 | **31.22** |
| ILA Los Menucos | −20.53 | **31.92** |
| ILA M. Ramos Mexía | −25.70 | **26.75** |
| ILA Nahuel Niyeu | −18.18 | **34.27** |
| Preamp Aguada Cecilio | −21.70 | **30.75** |

### Ecuación — OSNR acumulado de la red

$$
OSNR_{red} = -10 \cdot \log_{10}\left( \sum 10^{-OSNR_i/10} \right) = \mathbf{19.74} \text{ dB}
$$
*(Nota: El script `calc_rutas_gsnr.py` arroja un resultado final de OSNR ASE levemente inferior, **18.99 dB**, debido a penalidades y truncamientos de cálculo interno)*

### OSNR total combinando transceiver

$$
OSNR_{total} = -10 \cdot \log_{10}\left(10^{-38.0/10} + 10^{-18.99/10}\right) = \mathbf{18.94} \text{ dB}
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
| OSNR ASE | 18.99 dB |
| GSNR NLI | 43.96 dB |
| GSNR Total (Incluyendo TX OSNR 38dB) | **18.92 dB** |

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
| L total | 592.0 km | Suma de spans |

$$
CD_{acum} = 18.0 \times 592.0 = \mathbf{10656.0 \text{ ps/nm}}
$$

Este valor requerirá alta capacidad de compensación electrónica en el DSP (usualmente soportado por transceptores coherentes modernos para 100G).

---

## 6. PMD (Polarization Mode Dispersion)

### Ecuación

$$
PMD_{total} = \sqrt{\sum PMD_{fibra}^2 + \sum PMD_{ROADM}^2 + \sum PMD_{EDFA}^2}
$$

### Valores usados

| Elemento | PMD individual | Cantidad |
|----------|-------|--------|
| Fibra | 0.00126 ps/√km | 592 km |
| ROADM | 3.0 ps | 2 nodos (Tx y Rx) |
| EDFA | 3.0 ps | 8 amplificadores (Booster + 6 ILAs + Preamp) |

$$
PMD_{fibra\_sq} = (0.00126)^2 \times 592 \approx 0.0009 \text{ ps}^2
$$
$$
PMD_{equipos\_sq} = (2 \times 3.0^2) + (8 \times 3.0^2) = 18 + 72 = 90 \text{ ps}^2
$$
$$
PMD_{total} = \sqrt{0.0009 + 90} = \mathbf{9.48 \text{ ps}}
$$

El transceptor en 100/200G soporta este PMD sin aplicar penalidad observable (suele tolerar más de 20 ps).

---

## 7. PDL (Polarization Dependent Loss)

### Ecuación

$$
PDL_{total} \approx \sqrt{\sum PDL_i^2}
$$

### Valores usados y Resultado

| Elemento | PDL individual | Cantidad |
|----------|-------|--------|
| ROADM | 1.5 dB | 2 nodos |
| EDFA | 0.7 dB | 8 amplificadores |

$$
PDL_{total} = \sqrt{2 \times (1.5)^2 + 8 \times (0.7)^2} = \sqrt{4.5 + 3.92} = \mathbf{2.9 \text{ dB}}
$$

Al ser un PDL total inferior a 4 dB, no ejerce una gran penalidad en la relación final del enlace.

---

## 8. Comparativa y Explicación: 100 Gbps vs 200 Gbps

La gran diferencia entre establecer una comunicación de 100G o 200G sobre la misma fibra recae en el **formato de modulación** que el transceptor debe utilizar para empacar el doble de datos en el mismo tiempo (y mismo ancho de banda), y qué tanta pureza óptica (OSNR) necesita el receptor para interpretar esa señal sin errores (BER admisible).

| Capacidad | Modulación (Típica) | OSNR Requerido (puro) | Umbral Tolerable (con Margen 2dB) | GSNR de la Fibra | Margen Restante | ¿Factible? |
|-----------|--------------------|-----------------------|----------------------------------|------------------|----------------|-------------|
| **100 Gbps** | DP-QPSK | 12.8 dB | 14.8 dB | 18.92 dB | **+4.12 dB** | **SÍ (Holgado)** |
| **200 Gbps** | DP-8QAM / DP-16QAM | 21.5 dB | 23.5 dB | 18.92 dB | **-4.58 dB** | **NO** |

### ¿Por qué NO se puede llevar a cabo el enlace con 200 Gbps?

1. **Exigencia de la Constelación (Modulación):** Para transmitir 200 Gbps se usan constelaciones más densas (ej. 8QAM o 16QAM). El receptor requiere una señal sumamente nítida (OSNR mínimo 21.5 dB) para no confundir un punto con su vecino a causa del ruido térmico natural del amplificador (ruido ASE).
2. **Limitación Física del Enlace (GSNR = 18.92 dB):** A lo largo de los 592 km, la cascada de 8 amplificadores inyecta ruido ASE. El primer span de 107 km es el más crítico porque atenúa fuertemente la señal, y el ruido térmico que el primer ILA inyecta contamina irremediablemente el OSNR.
3. **Imposibilidad Matemática:** Como $18.92 \text{ dB} < 23.5 \text{ dB}$, el receptor leerá un nivel de errores en los bits (BER) imposible de corregir por los algoritmos de FEC.

---

## 9. Presupuesto de Potencia (Nodo a Nodo)

En las estaciones repetidoras (ILAs), los amplificadores compensan la atenuación del tramo anterior, pero están limitados físicamente a un rango de ganancia de entre 15 dB y 25 dB.

| Origen | Ganancia EDFA | Atenuación Tramo (Fibra) | Destino (Siguiente Nodo) | $P_{in}$ al EDFA dest. | $P_{out}$ del EDFA dest. |
|--------|---------------|--------------------------|--------------------------|------------------------|--------------------------|
| **Tx (ROADM Dina Huapi)** | - | - | **Booster Dina Huapi** | -20.00 dBm | -2.00 dBm (fija a 18 dB)|
| Booster Dina Huapi | 18.00 dB | -25.64 dB (107 km) | **ILA Comallo** | -27.64 dBm | -2.64 dBm (clipping a 25 dB)|
| ILA Comallo | 25.00 dB | -22.82 dB (95 km) | **ILA Ing. Jacobacci** | -25.46 dBm | -2.64 dBm (G = 22.82 dB) |
| ILA Ing. Jacobacci | 22.82 dB | -18.59 dB (77 km) | **ILA Maquinchao** | -21.23 dBm | -2.64 dBm (G = 18.59 dB) |
| ILA Maquinchao | 18.59 dB | -17.89 dB (74 km) | **ILA Los Menucos** | -20.53 dBm | -2.64 dBm (G = 17.89 dB) |
| ILA Los Menucos | 17.89 dB | -23.06 dB (96 km) | **ILA M. Ramos Mexía**| -25.70 dBm | -2.64 dBm (G = 23.06 dB) |
| ILA M. Ramos Mexía | 23.06 dB | -15.54 dB (64 km) | **ILA Nahuel Niyeu** | -18.18 dBm | -2.64 dBm (G = 15.54 dB) |
| ILA Nahuel Niyeu | 15.54 dB | -19.06 dB (79 km) | **Preamp Aguada Cecilio**| -21.70 dBm | -2.64 dBm (G = 19.06 dB) |

Al llegar al nodo receptor, el Preamp amplifica la señal para entregarla al receptor coherente, y luego el ROADM vuelve a atenuar/ecualizar el canal al target de **-20 dBm**.

**Nota técnica:** Observamos el efecto de *clipping* (saturación) de ganancia en el **ILA de Comallo**. Como el primer tramo atenuó 25.64 dB, el ILA debería proveer 25.64 dB de ganancia para volver a -2.0 dBm, pero su límite máximo de diseño es 25.0 dB. Esto produce que la potencia caiga a -2.64 dBm para el resto de la traza óptica, empeorando el OSNR.
