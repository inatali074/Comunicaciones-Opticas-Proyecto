# Cálculo de Extremos de Longitud de Onda

Este documento detalla el procedimiento para calcular las longitudes de onda extremas a partir de un ancho de banda espectral dado en frecuencia, asumiendo que la relación no es lineal.

## Datos Iniciales

*   **Longitud de onda central ($\lambda_0$):** $1550 \text{ nm}$
*   **Ancho de banda espectral total ($\Delta f$):** $3800 \text{ GHz}$

> [!WARNING]
> **Ojo importante:**
> El ancho de banda está dado en frecuencia, pero queremos encontrar los extremos en longitud de onda. Dado que la relación entre longitud de onda y frecuencia no es lineal ($c = \lambda \cdot f$), debemos usar la aproximación diferencial para pequeños cambios:
> 
> $$ \Delta\lambda \approx \frac{\lambda^2}{c} \cdot \Delta f $$

## Procedimiento de Cálculo

Primero, convertimos todas las magnitudes al Sistema Internacional (SI):

*   $\lambda_0 = 1550 \text{ nm} = 1.55 \times 10^{-6} \text{ m}$
*   $\Delta f = 3800 \text{ GHz} = 3.8 \times 10^{12} \text{ Hz}$
*   $c = 3 \times 10^8 \text{ m/s}$

### 1. Cálculo de $\Delta\lambda$ (Ancho Total en Longitud de Onda)

Reemplazando en la fórmula diferencial:

$$ \Delta\lambda \approx \frac{(1.55 \times 10^{-6})^2}{3 \times 10^8} \cdot (3.8 \times 10^{12}) $$

$$ \Delta\lambda \approx 30.4 \text{ nm} $$

Este es el **ancho total**. Para encontrar los extremos desde el centro, necesitamos la mitad de este valor:

$$ \frac{\Delta\lambda}{2} \approx 15.2 \text{ nm} $$

### 2. Longitudes de Onda Extremas

Restando y sumando la mitad del ancho de banda a la longitud de onda central:

*   **$\lambda$ mínima:**
    $$ 1550 - 15.2 \approx 1534.8 \text{ nm} $$

*   **$\lambda$ máxima:**
    $$ 1550 + 15.2 \approx 1565.2 \text{ nm} $$

---

## 🎯 Resultado Final

El sistema cubre aproximadamente el siguiente espectro óptico:

**$$ 1535 \text{ nm} \text{ a } 1565 \text{ nm} $$**

---

## 📈 Gráfica de Dispersión

A continuación, se muestra la gráfica de la Dispersión Cromática $D(\lambda)$ calculada para este mismo rango de operación, indicando los extremos que acabamos de obtener (1534.8 nm y 1565.2 nm) junto a la longitud de onda central de 1550 nm:

![](/home/santi/Descargas/descarga.png)
