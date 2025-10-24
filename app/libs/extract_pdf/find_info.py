import re

class Find_info:

    def find_supplier_name(line):
        if "Company:" in line:
            supplier_with_code = line.split("Company:")[1].strip()
            
            supplier = supplier_with_code.split('(')[0].strip()

            return supplier
        return None

    def find_product_info(line):
        if re.match(r'^\d{2}\s+', line.strip()):
            parts = line.split()
        
            product = parts[0]  
            erp_pattern = r'^\d{9}$'
            for part in parts:
                cleam_part = str(part).strip()
                if re.match(erp_pattern, cleam_part):
                    erp_code = cleam_part
        
            desc_start = line.find('-')
            if desc_start != -1:
                description = line[desc_start + 1:].strip()
                
                part_number_match = re.search(r'PN:(\S+)', description)
                if part_number_match:
                    part_number = part_number_match.group(1) 
                    description = description.split()


                    for index, desc in enumerate(description):
                        if 'PN:' in desc:
                            description.pop(index)
                            
                    description = ' '.join(description)

                elif part_number_match == None:
                    description = description.split()
                    part_number = description[0]
                    description.pop(0)
                    description = ' '.join(description)

                else:
                    return None
                    
                
                
                if 'PN:' in part_number:
                    name = description.split('PN:')[0].strip().rstrip('-').strip()
                else:
                    name = description.rstrip('-').strip()
                return {
                    'product': product,
                    'name': name,
                    'part_number': part_number,
                    'erp_code': erp_code
                }
        
        return None
