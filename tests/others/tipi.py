import asyncio
import json
from app.libs.ncm.setup import get_ncm


# query_list = [
#     "Capacitor Eletrolítico de Alumínio, 10 µF, 100 V, ±20%, 2000 h @ 85°C, Radial SMD", # 8532.22.00
#     "Capacitor Cerâmico, 1 µF, 16 V, X7R, ±5%, SMD 0805, 125°C",  # 8532.24.10
#     "Capacitor Cerâmico Multicamadas, 0,000015 µF, 50 V, C0G, SMD 0603",  # 8532.24.10
#     "LED Verde, 2 mm, 5,2 mcd, 560 nm, SMD, If 20 mA, Vf 2,1 V, Ângulo 130°, Lente Dome",  # 8541.41.21
#     "LED Amarelo Unicolor, 580 nm, 2 pinos, SMD",  # 8541.41.21
#     "Conector USB 2.0 Tipo A, Fêmea, 4 vias, 2 mm, Solda RA, Through-Hole",  # 8536.90.40
#     "Indutor fixo SMD, 1 µH, 4,47 A, 23 mΩ",  # 8504.50.10
#     "Série 351, bloco de terminais plugável, passo 5,08 mm, reto, tipo plug, montagem em cabo, 2 vias",  # 8536.90.40
#     "Série 351, Conector de Bloco de Terminais Plugável, Passo 5,08 mm, Reto, Tipo Plug, Montagem em Cabo, 2 Vias",  # 8536.90.90
#     "Antena LTE de banda larga com base magnética, cabo LL-195 de 3 m e conector SMA (694–894 / 1700–2700 MHz)"  # 8529.10.90 
# ]

query_list = [
    "Capacitor cerâmico 33pF 50V C0G 5% SMD 0603 125°C T/R",
    "Capacitor cerâmico 0.0047uF 50V X7R 10% SMD 0603 125°C T/R",
    "Capacitor cerâmico 18pF 50V C0G 5% SMD 0603 125°C T/R",
    "Capacitor cerâmico 10uF 10V X5R 10% SMD 0603 85°C T/R",
    "Capacitor cerâmico 10uF 25V X5R 20% SMD 0603 85°C T/R",
    # "NP0 PN:88512006119" Not found.
    "Capacitor eletrolítico de alumínio 10uF 100V ±20% 2000 horas @ 85°C radial SMD",
    "Resistor filme espesso 20KΩ 0.1W 1% SMD 0603 TCR 37 PPM/°C",
    "Resistor filme espesso 2.2KΩ 0.1W 1% SMD 0402",
    "Transistor bipolar silício NPN uso geral VCEO 45V IC 100mA PD 225mW SOT-23",
    "Transistor MOSFET P-CH silício 12V 4.3A 3 pinos SOT-23 T/R",
    "Diodo Schottky 100V 5A 3 pinos (2+aba) DPAK T/R",
    "Diodo supressor ESD TVS unidirecional 3.3V 3 pinos SOT-723 T/R",
    "Regulador LDO positivo 1.25V a 15V 1.2A 3 pinos (2+aba) DPAK T/R",
    "Oscilador XO 26MHz ±50ppm 15pF HCMOS 55% 3.3V automotivo AEC-Q200 4 pinos Mini-CSMD T/R"
]

async def main():
    results = []
    for query in query_list:
        result = await get_ncm(query)
        results.append(result)
    
    with open("ncm_text.json", "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)
    print("File JSON Tipi ")

if __name__ == "__main__":
    asyncio.run(main())