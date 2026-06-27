# Seguimiento de la Demanda de 400G Benavídez - Rosario (D196)

Este documento detalla el análisis de asignación espectral en la ruta norte para la demanda de **400G** entre **Benavídez** y **Rosario** (identificada en el tráfico base como **D196**). Se presenta la asignación tanto para el algoritmo **First-Fit** como para el algoritmo **Aleatorio (Random-Fit)**.

---

## 1. Resumen de la Demanda D196

* **Origen**: Benavídez (roadm Benavidez)
* **Destino**: Rosario (roadm Rosario)
* **Velocidad**: 400 Gbps
* **Slots Requeridos**: 6 slots (ancho de banda de 75 GHz en grilla flexible de 12.5 GHz)
* **Ruta Física Expandida (BFS)**:
  `roadm Benavidez` $\leftrightarrow$ `roadm Campana` $\leftrightarrow$ `roadm Zarate` $\leftrightarrow$ `roadm Baradero` $\leftrightarrow$ `roadm San Pedro BsAs` $\leftrightarrow$ `roadm San Nicolas de los Arroyos` $\leftrightarrow$ `roadm Rosario`

---

## 2. Asignación Espectral en Algoritmo First-Fit

El algoritmo **First-Fit** busca la primera ventana de 6 slots contiguos libres en toda la traza. Para la demanda D196, asignó el rango **S53 a S58** (Slots 53 a 58). 

A continuación se detalla el estado espectral en el entorno de la asignación (Slots S50 a S61):

| Enlace | S50 | S51 | S52 | S53 | S54 | S55 | S56 | S57 | S58 | S59 | S60 | S61 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Benavídez &rarr; Campana** | - | - | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | D198 | D198 | D198 |
| **Campana &rarr; Zárate** | D159 | D159 | D159 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | D198 | D198 | D198 |
| **Zárate &rarr; Baradero** | D159 | D159 | D159 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | D200 | D200 | D200 |
| **Baradero &rarr; San Pedro BsAs** | - | - | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | D200 | D200 | D200 |
| **San Pedro BsAs &rarr; San Nicolás** | - | - | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - |
| **San Nicolás &rarr; Rosario** | - | - | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - |

> [!NOTE]
> * **✅** representa la demanda bajo seguimiento: **D196** (400G).
> * **D159** representa la demanda *Campana-Baradero_100G_4*.
> * **D198** representa la demanda *Benavidez-Zarate_300G_1*.
> * **D200** representa la demanda *Zarate-SanPedro_300G_1*.
> * **-** representa un slot libre.

---

## 3. Asignación Espectral en Algoritmo Aleatorio (Random-Fit)

El algoritmo **Aleatorio (Random-Fit)** selecciona una ventana libre al azar dentro del espectro de manera uniforme. Para esta simulación, asignó el rango **S80 a S85** (Slots 80 a 85).

A continuación se detalla el estado espectral en el entorno de la asignación (Slots S77 a S88):

| Enlace | S77 | S78 | S79 | S80 | S81 | S82 | S83 | S84 | S85 | S86 | S87 | S88 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Benavídez &rarr; Campana** | - | - | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - |
| **Campana &rarr; Zárate** | - | - | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - |
| **Zárate &rarr; Baradero** | - | - | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - |
| **Baradero &rarr; San Pedro BsAs** | - | - | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - |
| **San Pedro BsAs &rarr; San Nicolás** | - | - | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - |
| **San Nicolás &rarr; Rosario** | - | - | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - |

---

## Conclusión

Ambas simulaciones lograron acomodar la demanda **D196** (400G) respetando la continuidad del espectro y la bidireccionalidad de los canales ópticos. 
* **First-Fit** la asignó de manera compacta en los slots más bajos disponibles (**S53-S58**) debido al tráfico precedente de las demandas D159, D198 y D200.
* **Aleatorio** seleccionó una ventana vacía en una posición más alta (**S80-S85**), dejando un espacio libre continuo a sus costados.
