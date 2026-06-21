import pandas as pd

nodes = ["Mendoza", "Tunuyan", "San Rafael", "Malargue", "Buta Ranquil", "Chos Malal", "Zapala", "Junin de los Andes", "San Martin de los Andes", "Villa La Angostura", "Dina Huapi", "San Carlos de Bariloche", "El Foyel", "Epuyen", "Esquel", "Tecka", "J. de San Martin", "Alto Rio Senguer", "Rio Mayo", "Perito Moreno", "Bajo Caracoles", "Gobernador Gregores", "Tres lagos", "El Calafate", "Esperanza (StaCruz)", "Rio Gallegos"]

def get_table(csv_file, start_s, end_s, assign_s_start, assign_s_end):
    df = pd.read_csv(csv_file)
    print(f"| Salto | Enlace | " + " | ".join([f"S{i}" for i in range(start_s, end_s+1)]) + " |")
    print(f"|:---:|:---|" + "|:---:" * (end_s - start_s + 1) + "|")
    
    for i in range(len(nodes)-1):
        origen = f"roadm {nodes[i]}"
        destino = f"roadm {nodes[i+1]}"
        
        row = df[(df["Nodo_Origen"] == origen) & (df["Nodo_Destino"] == destino)]
        if len(row) == 0:
            row = df[(df["Nodo_Origen"] == destino) & (df["Nodo_Destino"] == origen)]
            
        if len(row) == 0:
            vals = ["N/A"] * (end_s - start_s + 1)
        else:
            row = row.iloc[0]
            vals = []
            for s in range(start_s, end_s+1):
                val = str(row[f"Slot_{s}"])
                if val == "nan" or val == "":
                    vals.append("libre")
                elif assign_s_start <= s <= assign_s_end and val == "roadm Mendoza-roadm Rio Gallegos_400G_ref197":
                    vals.append("**REF197**")
                else:
                    parts = val.split("-")
                    vals.append(parts[0].replace("roadm ", "")[:8] if len(parts)>0 else val[:8])
        print(f"| {i+1} | {nodes[i]} → {nodes[i+1]} | " + " | ".join(vals) + " |")

print("--- FF ---")
get_table("Pablo_punto5/refefo/first_fit/ocupacion_refefo_firstfit.csv", 97, 110, 101, 106)
print("--- ALE ---")
get_table("Pablo_punto5/refefo/aleatorio/ocupacion_refefo_random.csv", 258, 271, 262, 267)
