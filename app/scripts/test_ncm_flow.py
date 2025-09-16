from app.db.chroma_db.data.tipi import fetch_ncm_data
from app.db.chroma_db.chromadb_manager import chroma_manager
from app.db.chroma_db.model import Response

fake_descriptions = [
    "Capacitor eletrolítico de alumínio, 10 uF, 100 V, ±20%, 2000 horas a 85°C, Radial Can - SMD",  # 8532.22.00
    "Capacitor cerâmico 1 uF, 16 V, X7R, 5%, encapsulamento 0805, até 125°C, montagem SMD (tape & reel)",  # 8532.24.10 ou 8532.25.10 / 8532.30.10
    "Diodo retificador em ponte, 1 kV, 2 A, 4 pinos, encapsulamento KBP, formato caixa",  
    "Transistor MOSFET canal N, 200 V, 18 A, resistência 0.15 Ω, encapsulamento TO-263AB, montagem em superfície",  
    "Resistor de filme metálico, 10 kΩ, 1/4 W, tolerância ±1%, encapsulamento axial, uso geral",  
    "Transformador de potência, 500 VA, frequência 50/60 Hz, primário 220 V, secundário 24 V, encapsulado",  
]

fetch_ncm_data()
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


 