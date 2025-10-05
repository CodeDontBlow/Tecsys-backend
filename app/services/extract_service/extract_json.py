import json
from app.services.extract_service.find_info import Find_info

class Extract_json:

    def extract(txt):
        supplyer = None
        products = []
        
        for linha in txt.splitlines():
            if supplyer is None:
                supplyer = Find_info.find_supplyer_name(linha)
            
            product_info = Find_info.find_product_info(linha)
            if product_info:
                products.append(product_info)
        
        return {
            'supplyer': supplyer,
            'products': products
        }

    def return_Datajson(txt):
        data = Extract_json.extract(txt)
        
        
        result = {}
        for i, product in enumerate(data["products"], 1):
            result[f"mercadoria_{i:02d}"] = {
                "numero": product["mercadoria"],
                "nome": product["nome"],
                "part_number": product["part_number"],
                "codigo_erp": product["codigo_erp"]
            }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
