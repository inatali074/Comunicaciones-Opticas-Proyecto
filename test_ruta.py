import calc_rutas_gsnr as cr
path = cr.bfs_shortest_path('roadm Dina Huapi', 'roadm Aguada Cecilio')
print("CAMINO:", path)
for i in range(len(path)):
    print(path[i])
    if i < len(path)-1 and path[i].startswith('roadm') and path[i+1].startswith('roadm'):
        print("Wait, roadm to roadm directly?")
        
print("100G:")
cr.calcular_ruta(['Dina Huapi', 'Aguada Cecilio'], 100)
print("200G:")
cr.calcular_ruta(['Dina Huapi', 'Aguada Cecilio'], 200)

