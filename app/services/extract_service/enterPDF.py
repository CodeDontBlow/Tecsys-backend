import json
from app.services.extract_service.pdf2txt import pdf_to_text 
from app.services.extract_service.extract_json import Extract_json
from app.services.extract_service.find_info import Find_info

class EnterPDF:
    def __init__(self, path_pdf):
        self.path_pdf = path_pdf
        self.text = None
        self.data = None
    
    def process_enter(self):
        """Método principal de entrada"""
        self.text = pdf_to_text(self.path_pdf)
        self.data = json.loads(Extract_json.return_Datajson(self.text))

        return self.data
    
    def get_supplyer_name(self):
        return Find_info.find_supplyer_name(self.text)
    
    def get_erp_desc(self):
        desc ={mercadoria['numero']: mercadoria['nome'] for mercadoria in self.data.values()}
        return desc
    
    def get_pn(self):
        pn = {mercadoria['numero']: mercadoria['part_number'] for mercadoria in self.data.values()}
        return pn
    
    def get_erp_code(self):
        code = {mercadoria['numero']: mercadoria['codigo_erp'] for mercadoria in self.data.values()}
        return code

