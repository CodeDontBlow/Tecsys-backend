import json
from .find_info import Find_info

class Extract_json:

    def extract(txt):
        supplier = None
        products = []
        
        for linha in txt.splitlines():
            if supplier is None:
                supplier = Find_info.find_supplier_name(linha)
            
            product_info = Find_info.find_product_info(linha)
            if product_info:
                products.append(product_info)
        
        return {
            'supplier': supplier,
            'products': products
        }

    def return_Datajson(txt):
        data = Extract_json.extract(txt)
        
        
        result = {}
        for i, product in enumerate(data["products"], 1):
            result[f"product_{i:02d}"] = {
                "number": product["product"],
                "name": product["name"],
                "part_number": product["part_number"],
                "erp_code": product["erp_code"]
            }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
