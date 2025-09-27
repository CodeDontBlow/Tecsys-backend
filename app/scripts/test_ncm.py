from app.services.ncm_service import get_ncm
import json

descriptions_pt = [

    # exemplos do primeiro excel
    "Capacitor Eletrolítico de Alumínio, 10 µF, 100 V, ±20%, 2000 h @ 85°C, Radial SMD",  # 8532.22.00
    "Capacitor Cerâmico, 1 µF, 16 V, X7R, ±5%, SMD 0805, 125°C",  # 8532.24.10

    # exemplos do segundo excel
    "Capacitor Cerâmico Multicamadas, 0,000015 µF, 50 V, C0G, SMD 0603",  # 8532.24.10
    "LED Verde, 2 mm, 5,2 mcd, 560 nm, SMD, If 20 mA, Vf 2,1 V, Ângulo 130°, Lente Dome",  # 8541.41.21
    "LED Amarelo Unicolor, 580 nm, 2 pinos, SMD",  # 8541.41.21
    "Conector USB 2.0 Tipo A, Fêmea, 4 vias, 2 mm, Solda RA, Through-Hole",  # 8536.90.40
]

# TEST SERVICE
for description in descriptions_pt:
    result = get_ncm(description)
    print(json.dumps(result, indent=3, ensure_ascii=False))