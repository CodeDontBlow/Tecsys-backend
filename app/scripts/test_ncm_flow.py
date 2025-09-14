from pathlib import Path
from app.util.ncm import fetch_ncm_data
from app.db.chroma_db.chroma_functions import create_collection, populate_collection, search_in_collection

#run: python -m app.scripts.test_ncm_flow 
#ou
#run: python3 -m app.scripts.test_ncm_flow 

fetch_ncm_data()
collection = create_collection("ncm_85")

path_csv = "app/data/ncm_chapter_85.csv"
populate_collection(path_csv, collection)

fake_descriptions = [
    "Domestic power transformer 500VA",
    "Portable 3kW generator",
    "Wall switch for lighting",
    "Residential distribution panel",
    "Three-phase electric motor 2HP",
    "Control board for solar inverter",
    "10A thermal-magnetic circuit breaker",
    "Ignition coil for electrical equipment",
    "High-voltage power cable",
    "Industrial current sensor"
]

for description in fake_descriptions:
    result = search_in_collection(collection, description, 1)
    
    document = result['documents'][0][0] 
    codigo_ncm = result['metadatas'][0][0]['codigo_ncm']  
    distancia = result['distances'][0][0]

    print("\nSearch results:")
    print(
        f"document: {document}\n"
        f"codigo_ncm: {codigo_ncm}\n"
        f"distancia: {distancia}\n"
    )
