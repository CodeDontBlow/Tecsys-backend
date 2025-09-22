import re

class Find_info:

    def find_company_name(linha):
        if "Company:" in linha:
            company_with_code = linha.split("Company:")[1].strip()
            
            company = company_with_code.split('(')[0].strip()

            return company
        return None

    def find_product_info(linha):
        if re.match(r'^\d{2}\s+', linha.strip()):
            partes = linha.split()
            
            if len(partes) >= 10:
                mercadoria = partes[0]  
                codigo_company = partes[6]  
                
            
                desc_start = linha.find('-')
                if desc_start != -1:
                    descricao = linha[desc_start + 1:].strip()
                    
                    part_number_match = re.search(r'PN:(\S+)', descricao)
                    if part_number_match:
                        part_number = part_number_match.group(1) 
                        descricao = descricao.split()


                        for index, desc in enumerate(descricao):
                            if 'PN:' in desc:
                                descricao.pop(index)
                                
                        descricao = ' '.join(descricao)

                    elif part_number_match == None:
                        descricao = descricao.split()
                        part_number = descricao[0]
                        descricao.pop(0)
                        descricao = ' '.join(descricao)

                    else:
                        return None
                        
                    
                    
                    if 'PN:' in part_number:
                        nome = descricao.split('PN:')[0].strip().rstrip('-').strip()
                    else:
                        nome = descricao.rstrip('-').strip()
                    return {
                        'mercadoria': mercadoria,
                        'nome': nome,
                        'part_number': part_number,
                        'codigo_company': codigo_company
                    }
        
        return None
