def translate_electronics_terms(query: str) -> str:
    translation_map = {
        "capacitor": "capacitor", "ceramic": "cerâmica", "electrolytic": "eletrolítico",
        "aluminum": "alumínio", "multilayer": "multicamada", "radial": "radial",
        "smd": "montagem em superfície", "axial": "axial", "voltage": "tensão",
        "capacitance": "capacitância", "tolerance": "tolerância", "hours": "horas",
        "resistor": "resistor", "ohm": "ohm", "watt": "watt", "precision": "precisão",
        "component": "componente", "electronic": "eletrônico", "metric": "métrico",
    }
    
    new_query = query.lower()
    for eng, por in translation_map.items():
        if eng in new_query:
            new_query += f" {por}"    
    return new_query


def format_query_for_ncm(query: str) -> str:
    translated_query = translate_electronics_terms(query)
    
    return f"""
    Buscar classificação fiscal NCM para componente eletrônico: {translated_query}
    Categoria: Capacitores Resistores Diodos Transistores Circuitos Integrados
    Tipo: Eletrônico Semicondutor Dispositivo Eletrônico
    Aplicação: Importação Classificação Fiscal NCM
    """

def detect_query_category(query: str) -> str:
    query_lower = query.lower()

    category_list = {
        "capacitor": {"capacitor", "cap", "uf", "μf", "pf"},
        "resistor": {"resistor", "res", "ohm", "kohm", "mohm"},
        "diodo": {"diode", "diodo", "led", "zener"},
        "transistor": {"transistor", "fet", "mosfet", "bjt"},
        "circuito integrado": {"ic", "circuit", "integrated", "chip"},
    }

    for category, keywords in category_list.items():
        if any(key in query_lower for key in keywords):
            return category
    return "eletronico_geral"





