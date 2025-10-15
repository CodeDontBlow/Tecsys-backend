import json
from app.services.ncm_service import get_ncm

descriptions_pt = [
    "Capacitor Eletrolítico de Alumínio, 10 µF, 100 V, ±20%, 2000 h @ 85°C, Radial SMD", # 8532.22.00
    "Capacitor Cerâmico, 1 µF, 16 V, X7R, ±5%, SMD 0805, 125°C",  # 8532.24.10
    "Capacitor Cerâmico Multicamadas, 0,000015 µF, 50 V, C0G, SMD 0603",  # 8532.24.10
    "LED Verde, 2 mm, 5,2 mcd, 560 nm, SMD, If 20 mA, Vf 2,1 V, Ângulo 130°, Lente Dome",  # 8541.41.21
    "LED Amarelo Unicolor, 580 nm, 2 pinos, SMD",  # 8541.41.21
    "Conector USB 2.0 Tipo A, Fêmea, 4 vias, 2 mm, Solda RA, Through-Hole",  # 8536.90.40
    "Indutor fixo SMD, 1 µH, 4,47 A, 23 mΩ",  # 8504.50.10
    "Série 351, bloco de terminais plugável, passo 5,08 mm, reto, tipo plug, montagem em cabo, 2 vias",  # 8536.90.40
    "Série 351, Conector de Bloco de Terminais Plugável, Passo 5,08 mm, Reto, Tipo Plug, Montagem em Cabo, 2 Vias",  # 8536.90.90
    "Antena LTE de banda larga com base magnética, cabo LL-195 de 3 m e conector SMA (694–894 / 1700–2700 MHz)"  # 8529.10.90
]


for description in descriptions_pt:
    print(f"=== Testing description: {description} ===")
    result = get_ncm(description)
    print(json.dumps(result, indent=3, ensure_ascii=False))
    print("\n")
