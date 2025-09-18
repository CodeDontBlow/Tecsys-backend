from app.db.chroma_db.tipi import fetch_ncm_data
from app.db.chroma_db.chromadb_manager import chroma_manager
from app.db.chroma_db.model import Response

fetch_ncm_data()

fake_descriptions = [
    "Capacitor eletrolítico de alumínio, 10 uF, 100 V, ±20%, 2000 horas a 85°C, Radial Can - SMD", 
    "Capacitor cerâmico 1 uF, 16 V, X7R, 5%, encapsulamento 0805, até 125°C, montagem SMD (tape & reel)",  
    "Diodo retificador em ponte, 1 kV, 2 A, 4 pinos, encapsulamento KBP, formato caixa",  
    "Conector HDMI, 19 pinos, passo de 0,5 mm, solda RA, SMD, porta única em bandeja", 
    "Conector para placas empilháveis, série DW, 1 contato, conector tipo header, through-hole, 1 fila", 
    "Capacitor cerâmico multicamadas, 10 pF, 25 V, ±0,5 pF, tipo C0G (NP0), encapsulamento 0201 [0603 métrico]", 
    "Sensor de luz ambiente, infravermelho, analógico, solda, tensão de operação 2,5 a 5,5 V",
    "Transdutor de áudio eletromagnético, 1,5 Vp-p, 10 mA, pino 1 Vp-p, 1548 Hz a 2548 Hz, through-hole", 
    "Retificador padrão, 400 V, 1,0 A",  
    "Driver de gate, 1 canal, isolado, high side, IGBT, MOSFET Si e SiC, 8 pinos, DSO" 
]

chroma_manager.populate_from_csv()

def print_response(response: Response):
    print(f"Query: {response.query}\n")
    for r in response.result:
        print(f"NCM Code   : {r.ncm_code}")
        print(f"Description: {r.description}")
        print(f"Distance   : {r.distance:.4f}")
        print("-" * 80)  

for query in fake_descriptions:
    response = chroma_manager.search_ncm(query, n_results=1)
    print_response(response)


 