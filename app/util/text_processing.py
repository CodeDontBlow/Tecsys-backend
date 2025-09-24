def formated_query(query: str) -> str:
    """
    Recebe uma descrição e retorna uma query enriquecida para embedding,
    incluindo termos-chave detectados em diferentes categorias.
    """
    termos_chave = {
        "geral": ["outros", "aparelhos", "elétricos", "superior", "inferior", "tipo", "mesmo",
                  "montados", "incluindo", "exceto", "partes", "montagem", "do", "uma", "que"],
        "eletronicos": ["diodo", "led", "circuito", "transistor", "resistencia", "condensador",
                        "capacitor", "semicondutor", "dispositivo", "integrado", "memoria",
                        "eprom", "eeprom", "flash", "smd", "chipset", "driver", "controlador",
                        "sensor", "microfone", "altofalante", "amplificador", "receptor", "transmissor"],
        "eletricos": ["motor", "gerador", "transformador", "bobina", "tubo", "pilha", "bateria",
                      "fusivel", "disjuntor", "condutor", "cabo", "conector", "painel", "chave",
                      "interruptor", "lampada"],
        "comunicacao": ["televisao", "radio", "telefone", "antena", "modem", "roteador", "hub",
                        "switch", "sinal", "repetidor", "satelite", "transmissao"],
        "medidas": ["v", "kw", "kva", "w", "cm", "mm", "hz", "ghz", "m", "ah", "kg", "lux", "khz", "nm"],
        "materiais": ["cobre", "ferro", "aluminio", "plastico", "vidro", "ceramica", "resina",
                      "cadmio", "chumbo", "mercurio", "policlorobifenilas", "tantalo"],
        "outras_funcoes": ["aquecimento", "iluminacao", "ar", "refrigeracao", "energia", "controle",
                           "processamento", "armazenamento", "visualizacao", "captura", "deteccao",
                           "regulacao", "protecao", "isolante", "conexao", "suporte", "medicao",
                           "conversores"]
    }

    words = query.lower().replace(",", " ").replace("(", " ").replace(")", " ").split()
    detected_terms = []

    for cat_terms in termos_chave.values():
        for term in cat_terms:
            if term in words:
                detected_terms.append(term)

    return query + " " + " ".join(detected_terms)











