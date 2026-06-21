import matplotlib.pyplot as plt
import numpy as np
import os

# Create directory if it doesn't exist
os.makedirs('/home/nacho/Escritorio/Comunicaciones Opticas/trabajo final/Main/TpOpticas/Analisis_Nodo_Cordoba', exist_ok=True)
base_path = '/home/nacho/Escritorio/Comunicaciones Opticas/trabajo final/Main/TpOpticas/Analisis_Nodo_Cordoba/'

# Estilo profesional
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    plt.style.use('ggplot')

# ==========================================
# 1. Gráfico de Ocupación (Base vs REFEFO)
# ==========================================
enlaces = ['Corralito', 'Arroyito', 'Manfredi', 'Jesús María', 'La Falda', 'Serrezuela', 'La Rioja', 'Patquía', 'V. Mercedes']
base_slots = [76, 28, 64, 36, 36, 20, 12, 4, 4]
refefo_slots = [152, 140, 110, 78, 60, 20, 12, 10, 4]

x = np.arange(len(enlaces))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 6))
rects1 = ax.bar(x - width/2, base_slots, width, label='Tráfico Base', color='#3498db')
rects2 = ax.bar(x + width/2, refefo_slots, width, label='Base + REFEFO', color='#e74c3c')

# Línea de límite de fibra (304 slots)
ax.axhline(y=304, color='black', linestyle='--', alpha=0.7, label='Capacidad Máx (304 Slots)')

ax.set_ylabel('Slots Ocupados')
ax.set_title('Saturación de Espectro en Córdoba (Base vs REFEFO)')
ax.set_xticks(x)
ax.set_xticklabels(enlaces, rotation=30, ha="right")
ax.legend()

# Etiquetas sobre barras
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)

autolabel(rects1)
autolabel(rects2)

plt.tight_layout()
plt.savefig(base_path + 'grafico_ocupacion.png', dpi=300)
plt.close()

print("Grafico de ocupacion generado exitosamente.")
