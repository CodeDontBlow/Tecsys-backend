import re

class Find_info:

    def find_supplier_name(linha):
        if "Company:" in linha:
            supplier_with_code = linha.split("Company:")[1].strip()
            
            supplier = supplier_with_code.split('(')[0].strip()

            return supplier
        return None

    def find_product_info(linha):
        if re.match(r'^\d{2}\s+', linha.strip()):
            partes = linha.split()

            mercadoria = partes[0]  

            padrão_erp = r'^\d{9}$'
            for parte in partes:
                parte_limpa = str(parte).strip()
                if re.match(padrão_erp, parte_limpa):
                    codigo_erp = parte_limpa
            
        
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
                    'codigo_erp': codigo_erp
                }
        
        return None
