from app.db.chroma_db.data.tipi import fetch_ncm_data
from app.db.chroma_db.chromadb_manager import chroma_manager
from app.db.chroma_db.model import Response

fake_descriptions = [
    "Aluminum Electrolytic Capacitor, 10 uF, 100 V, ± 20%, 2000 hours @ 85°C, Radial Can - SMD", #8532.22.00 
    "Cap Ceramic 1uF 16V X7R 5% Pad SMD 0805 125°C T/R", #8532.24.10 ou #8532.25.10  8532.30.10 
    "Rectifier Bridge Diode Single 1KV 2A 4-Pin Case KBP Box", #8541.10 
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


 