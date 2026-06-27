# Formulación Matemática y Modelado Físico para el Diseño de Redes Ópticas DWDM Coherentes

Este documento reúne las ecuaciones fundamentales empleadas para el modelado físico de los enlaces de fibra, el balance de potencias, la generación de ruido lineal (ASE), los efectos no lineales (NLI), la dispersión cromática (CD) y la relación señal-ruido generalizada (GSNR) que gobierna la calidad de transmisión (QoT) de los canales elásticos del proyecto.

---

## 1. Balance de Potencia Óptica Tramo a Tramo

El balance de potencias a lo largo de un canal óptico (lightpath) modela la evolución de la potencia media del canal por portadora en cada componente de la red.

### 1.1. Atenuación del Vano de Fibra (Span)
La pérdida de potencia en un tramo de fibra monomodo de longitud $L$ se calcula como:
$$A_{\text{span}} \text{ [dB]} = \alpha \cdot L + A_{\text{empalmes}}$$

Donde:
* $\alpha$: Coeficiente de atenuación lineal de la fibra ($\text{dB/km}$). Para la Corning® SMF-28® Ultra con empalmes por fusión de diseño, se utiliza $\alpha = 0.185 \text{ dB/km}$.
* $L$: Longitud física del tramo ($\text{km}$).
* $A_{\text{empalmes}}$: Pérdidas adicionales por conectores y empalmes intermedios.

### 1.2. Potencia de Entrada y Salida en Amplificadores
En amplificadores ópticos (booster, amplificadores de línea ILA y preamplificadores), la relación de potencias en escala logarítmica es:
$$P_{\text{out}} \text{ [dBm]} = P_{\text{in}} \text{ [dBm]} + G \text{ [dB]}$$

Donde:
* $P_{\text{in}}$: Potencia total o por canal a la entrada del amplificador.
* $P_{\text{out}}$: Potencia a la salida.
* $G$: Ganancia del amplificador, limitada por la potencia de salida en saturación del equipo ($P_{\text{sat}} = +21.5 \text{ dBm}$ para el OLA2525).

### 1.3. Potencia Recibida en el Extremo Rx
La potencia que ingresa al receptor coherente tras atravesar la red y el demultiplexor terminal se expresa como:
$$P_{\text{rx}} \text{ [dBm]} = P_{\text{Tx}} \text{ [dBm]} - A_{\text{MUX}} + G_{\text{booster}} - \sum A_{\text{spans}} + \sum G_{\text{ILAs}} + G_{\text{preamp}} - A_{\text{DEMUX}} - A_{\text{VOA}}$$

---

## 2. Generación de Ruido Lineal: Emisión Espontánea Amplificada (ASE)

Los amplificadores ópticos de fibra dopada con erbio (EDFA) introducen ruido debido al proceso de emisión espontánea amplificada.

### 2.1. Potencia de Ruido ASE de un Amplificador
La potencia de ruido ASE generada por un único amplificador $i$ en un ancho de banda de referencia $B_{\text{ref}}$ (típicamente $12.5 \text{ GHz}$ o $0.1 \text{ nm}$ a una longitud de onda de $1550 \text{ nm}$) se calcula en escala lineal mediante:
$$P_{\text{ASE}, i} \text{ [W]} = h \cdot \nu \cdot NF_i \cdot (G_i - 1) \cdot B_{\text{ref}}$$

Donde:
* $h$: Constante de Planck ($6.626 \times 10^{-34} \text{ J}\cdot\text{s}$).
* $\nu$: Frecuencia óptica central del canal ($\text{Hz}$). A $1550 \text{ nm}$, $\nu \approx 193.1 \text{ THz}$.
* $NF_i$: Figura de ruido del amplificador en escala lineal ($NF_{\text{lineal}} = 10^{(NF_{\text{dB}} / 10)}$).
* $G_i$: Ganancia del amplificador en escala lineal ($G_{\text{lineal}} = 10^{(G_{\text{dB}} / 10)}$).
* $B_{\text{ref}}$: Ancho de banda de resolución del receptor de ruido ($12.5 \text{ GHz}$).

### 2.2. Relación Señal-Ruido Óptica Lineal (OSNR ASE)
El ruido ASE acumulado a lo largo de un enlace de $N$ amplificadores es la suma de las potencias de ruido individuales:
$$P_{\text{ASE, total}} \text{ [W]} = \sum_{i=1}^{N} P_{\text{ASE}, i}$$

La OSNR lineal (debida únicamente al ruido ASE) se define como:
$$\text{OSNR}_{\text{ASE}} = \frac{P_{\text{ch}}}{P_{\text{ASE, total}}}$$

En escala logarítmica (dB):
$$\text{OSNR}_{\text{ASE}} \text{ [dB]} = 10 \cdot \log_{10} \left( \frac{P_{\text{ch}} \text{ [W]}}{P_{\text{ASE, total}} \text{ [W]}} \right)$$

---

## 3. Ruido No Lineal: Interferencia No Lineal (NLI)

Los efectos no lineales de tercer orden (efecto Kerr), tales como la automodulación de fase (SPM) y la modulación de fase cruzada (XPM), se modelan matemáticamente como una fuente de ruido gaussiano aditivo e independiente, conocida como interferencia no lineal (NLI).

### 3.1. Potencia de Ruido NLI por Vano (Modelo GN)
Bajo la aproximación del Modelo de Ruido Gaussiano (GN-Model) para fibras con dispersión cromática acumulada significativa, la potencia de ruido NLI acumulada en un vano se modela como:
$$P_{\text{NLI}} \text{ [W]} = \eta_{\text{NLI}} \cdot P_{\text{ch}}^3$$

Donde:
* $P_{\text{ch}}$: Potencia óptica del canal a la entrada de la fibra ($\text{W}$).
* $\eta_{\text{NLI}}$: Coeficiente de eficiencia no lineal del tramo ($\text{W}^{-2}$).

### 3.2. Coeficiente de Eficiencia No Lineal ($\eta_{\text{NLI}}$)
Para un canal central en un sistema de transmisión elástica y multi-canal, el coeficiente de eficiencia no lineal se aproxima analíticamente mediante la ecuación:
$$\eta_{\text{NLI}} \approx \frac{8}{27} \cdot \gamma^2 \cdot \frac{A_{\text{eff-para-NLI}}}{\pi \cdot |\beta_2| \cdot \alpha} \cdot \text{asinh} \left( \frac{\pi^2}{2} \cdot \frac{|\beta_2|}{\alpha} \cdot B_{\text{ch}}^2 \cdot N_{\text{ch}}^{2 \cdot \frac{B_{\text{ch}}}{\Delta f}} \right)$$

Donde:
* $\gamma$: Coeficiente de no linealidad Kerr de la fibra ($\text{W}^{-1}\text{km}^{-1}$). Para la SMF-28, $\gamma = 1.3 \text{ W}^{-1}\text{km}^{-1}$.
* $\beta_2$: Parámetro de dispersión de velocidad de grupo ($\text{s}^2\text{/km}$), relacionado con el parámetro de dispersión $D$ por:
  $$\beta_2 = -\frac{\lambda^2}{2\pi \cdot c} \cdot D$$
  *(a $1550 \text{ nm}$ con $D = 18 \text{ ps/(nm}\cdot\text{km)}$, $\beta_2 \approx -22.9 \text{ ps}^2\text{/km}$)*.
* $\alpha$: Coeficiente de atenuación de la fibra en escala lineal de atenuación espacial ($\text{rad/km}$), definido como $\alpha_{\text{lineal}} = \alpha_{\text{dB/km}} / 4.343$.
* $B_{\text{ch}}$: Ancho de banda espectral ocupado por el canal u tasa de símbolos ($\text{Hz}$).
* $N_{\text{ch}}$: Número total de canales activos en la banda.
* $\Delta f$: Espaciamiento de canales en la grilla espectral.

La OSNR no lineal se define como:
$$\text{OSNR}_{\text{NLI}} = \frac{P_{\text{ch}}}{P_{\text{NLI}}} = \frac{1}{\eta_{\text{NLI}} \cdot P_{\text{ch}}^2}$$

---

## 4. Relación Señal-Ruido Generalizada (GSNR)

La GSNR evalúa la calidad de transmisión de extremo a extremo del camino óptico combinando las contribuciones lineales y no lineales:

$$\text{GSNR}^{-1} = \text{OSNR}_{\text{ASE}}^{-1} + \text{OSNR}_{\text{NLI}}^{-1}$$

Expresada de forma explícita en potencia de señal y ruido:
$$\text{GSNR} = \frac{P_{\text{ch}}}{P_{\text{ASE, total}} + P_{\text{NLI, total}}}$$

En decibelios (dB):
$$\text{GSNR} \text{ [dB]} = 10 \cdot \log_{10} \left( \frac{P_{\text{ch}}}{P_{\text{ASE, total}} + P_{\text{NLI, total}}} \right)$$

Esta relación matemática demuestra que la GSNR presenta un comportamiento cóncavo (forma de parábola invertida) respecto de la potencia del canal $P_{\text{ch}}$:
* A potencias bajas, predomina el ruido ASE de los amplificadores (régimen limitado por ruido térmico/lineal).
* A potencias altas, predomina el ruido de NLI debido al término cúbico $P_{\text{ch}}^3$ (régimen limitado por no linealidades).
* Existe un punto de operación óptimo denominado **Potencia Óptima de Canal** que maximiza la GSNR.

---

## 5. Dispersión Óptica Acumulada

### 5.1. Dispersión Cromática (CD)
La dispersión cromática total acumulada a lo largo del trayecto óptico se calcula mediante la integración de las distancias de cada tramo:
$$CD_{\text{acumulada}} \text{ [ps/nm]} = \sum_{j=1}^{M} D_j \cdot L_j$$

Donde:
* $D_j$: Coeficiente de dispersión cromática de la sección de fibra $j$ ($\text{ps/(nm}\cdot\text{km)}$).
* $L_j$: Longitud de la sección de fibra $j$ ($\text{km}$).

La CD residual final que llega al receptor debe estar dentro de los límites de tolerancia de compensación electrónica del ecualizador DSP del transceptor óptico coherente (por ejemplo, $\pm 12,000 \text{ ps/nm}$ en Modo 6 a 400G).

### 5.2. Dispersión por Modo de Polarización (PMD)
La distorsión por modo de polarización acumulada en fibras ópticas largas sigue un comportamiento estadístico estocástico debido a las variaciones aleatorias de la birrefringencia a lo largo de la fibra. El valor medio cuadrático del retraso de grupo diferencial (DGD) acumulado se modela como:
$$PMD_{\text{acumulado}} \text{ [ps]} = PMD_{\text{link}} \cdot \sqrt{L_{\text{total}}}$$

Donde:
* $PMD_{\text{link}}$: Coeficiente de PMD del enlace ($\text{ps/}\sqrt{\text{km}}$). Para la SMF-28 Ultra, el valor de diseño del enlace es $PMD_{\text{link}} \le 0.04 \text{ ps/}\sqrt{\text{km}}$.
* $L_{\text{total}}$: Longitud total acumulada del enlace ($\text{km}$).
