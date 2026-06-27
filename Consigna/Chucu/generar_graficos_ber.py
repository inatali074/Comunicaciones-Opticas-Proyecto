import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc

# Configurar el estilo para que se vea premium (estilo oscuro/moderno o limpio)
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16
})

# Parámetros del gráfico
gsnr_db = np.linspace(5, 30, 500)
fec_threshold_ber = 1.5e-2  # Límite del FEC (BER Pre-FEC máximo)

# Q correspondiente al límite FEC
# erfc(Q/sqrt(2)) = 2 * BER => Q = sqrt(2) * erfinv(1 - 2*BER)
# Para BER = 0.015, Q es aprox 2.17
q_fec = 2.17

# offsets calculados para que al GSNR nominal, la BER sea exactamente fec_threshold_ber (Q = 2.17)
# offset_db = GSNR_req - 10 * log10(Q^2) = GSNR_req - 6.73
offsets = {
    "100G (DP-QPSK)": 11.8 - 6.73,
    "200G (DP-8QAM/QPSK-like)": 20.5 - 6.73,
    "300G (DP-8QAM)": 21.0 - 6.73,
    "400G (DP-16QAM)": 23.5 - 6.73
}

colors = {
    "100G (DP-QPSK)": "#007acc",
    "200G (DP-8QAM/QPSK-like)": "#228b22",
    "300G (DP-8QAM)": "#ff8c00",
    "400G (DP-16QAM)": "#d9534f"
}

plt.figure(figsize=(10, 6.5), dpi=300)

for label, offset in offsets.items():
    # Convertir GSNR a Q
    gsnr_linear = 10**((gsnr_db - offset)/10)
    q = np.sqrt(gsnr_linear)
    
    # Calcular BER
    ber = 0.5 * erfc(q / np.sqrt(2))
    
    # Graficar
    plt.semilogy(gsnr_db, ber, label=label, color=colors[label], linewidth=2.5)

# Graficar la línea de límite del FEC
plt.axhline(y=fec_threshold_ber, color='#444444', linestyle='--', linewidth=1.5, 
            label=f'Límite FEC (BER ≈ {fec_threshold_ber:.3f})')

# Marcar los puntos de factibilidad nominales en la línea del FEC
nominal_gsnrs = [11.8, 20.5, 21.0, 23.5]
labels = ["100G", "200G", "300G", "400G"]
for gsnr_val, col, lbl in zip(nominal_gsnrs, colors.values(), labels):
    plt.plot(gsnr_val, fec_threshold_ber, 'o', color=col, markersize=8, markeredgecolor='black', markeredgewidth=1)
    plt.annotate(f"{gsnr_val} dB", 
                 xy=(gsnr_val, fec_threshold_ber), 
                 xytext=(gsnr_val - 0.2, fec_threshold_ber * 1.5),
                 color=col,
                 weight='bold',
                 fontsize=9,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=col, lw=0.5, alpha=0.9))

# Ajustes de los ejes y diseño
plt.title("Probabilidad de Error de Bit (BER Pre-FEC) vs. GSNR", pad=15, weight='bold')
plt.xlabel("GSNR de Canal Recibido (dB)", labelpad=10)
plt.ylabel("Tasa de Error de Bit (BER)", labelpad=10)
plt.xlim(8, 28)
plt.ylim(1e-9, 1)
plt.legend(loc='lower left', frameon=True, facecolor='white', edgecolor='#cccccc', framealpha=0.9)



plt.tight_layout()

# Guardar la imagen
output_path = "ber_vs_gsnr.png"
plt.savefig(output_path, bbox_inches='tight')
print(f"Gráfico guardado en {output_path}")
