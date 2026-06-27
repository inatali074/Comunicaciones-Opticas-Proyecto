import csv
import matplotlib.pyplot as plt
import numpy as np

# Configurar estilo visual premium
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

csv_path = "../../resultados_gsnr_demandas_base.csv"

distances = {100: [], 200: [], 300: [], 400: []}
gsnrs = {100: [], 200: [], 300: [], 400: []}
colors = {100: "#007acc", 200: "#228b22", 300: "#ff8c00", 400: "#d9534f"}
thresholds = {100: 11.8, 200: 20.5, 300: 20.5, 400: 23.5}

# Leer y procesar datos del CSV
with open(csv_path, 'r', encoding='utf-8') as f:
    # El archivo usa tabulaciones (\t) como delimitador
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        try:
            vel = int(float(row["Velocidad [Gbps]"]))
            dist = float(row["Distancia_km"])
            gsnr = float(row["GSNR_Total_dB"])
            
            if vel in distances:
                distances[vel].append(dist)
                gsnrs[vel].append(gsnr)
        except Exception:
            # Ignorar filas con errores o encabezados incorrectos
            continue

plt.figure(figsize=(10, 6.5), dpi=300)

# Graficar los puntos de demandas reales
for vel in [100, 200, 300, 400]:
    if distances[vel]:
        plt.scatter(distances[vel], gsnrs[vel], 
                    color=colors[vel], label=f"Demandas {vel}G", 
                    alpha=0.7, edgecolors='none', s=40)

# Dibujar líneas de umbral para cada velocidad
# Para no sobrecargar el gráfico, solo graficamos los umbrales principales
plt.axhline(y=23.5, color=colors[400], linestyle='--', alpha=0.5, linewidth=1.2)
plt.text(1450, 24.0, "Umbral 400G (23.5 dB)", color=colors[400], fontsize=9, weight='bold')

plt.axhline(y=20.5, color=colors[200], linestyle='--', alpha=0.5, linewidth=1.2)
plt.text(1450, 19.5, "Umbral 200G/300G (20.5 dB)", color=colors[200], fontsize=9, weight='bold')

plt.axhline(y=11.8, color=colors[100], linestyle='--', alpha=0.5, linewidth=1.2)
plt.text(1450, 12.3, "Umbral 100G (11.8 dB)", color=colors[100], fontsize=9, weight='bold')

# Estética y límites
plt.title("GSNR vs. Distancia Física de Enlace (Resultados Simulados)", pad=15, weight='bold')
plt.xlabel("Distancia Física de Enlace (km)", labelpad=10)
plt.ylabel("GSNR Total de Canal Recibido (dB)", labelpad=10)
plt.xlim(0, 1700)
plt.ylim(5, 35)
plt.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='#cccccc', framealpha=0.9)

plt.tight_layout()

output_path = "gsnr_vs_distancia.png"
plt.savefig(output_path, bbox_inches='tight')
print(f"Gráfico guardado en {output_path}")
