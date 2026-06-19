import json

data = json.load(open('network_mashe.json'))
elements = {e['uid']: e for e in data['elements']}

fibers = [
    'fiber (Dina Huapi → Comallo)-',
    'fiber (Comallo → Ing. Jacobacci)-',
    'fiber (Ing. Jacobacci → Maquinchao)-',
    'fiber (Maquinchao → Los Menucos)-',
    'fiber (Los Menucos → Ministro Ramos Mexía)-',
    'fiber (Ministro Ramos Mexía → Nahuel Niyeu)-',
    'fiber (Nahuel Niyeu → Aguada Cecilio)-'
]

total_len = 0
for f in fibers:
    node = elements[f]
    length = node.get("length", node.get("params", {}).get("length", 0))
    loss = node.get("loss_coef", node.get("params", {}).get("loss_coef", 0.2))
    print(f"{f}: {length} km, loss {length*loss:.2f} dB + 0.5 = {(length*loss)+0.5:.2f} dB total")
    total_len += length
    
print("Total Length:", total_len)
