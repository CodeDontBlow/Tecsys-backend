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
        self.data = Extract_json.return_Datajson(self.text)
        return self.data
    
    def get_company_name(self):
        return Find_info.find_company_name(self.text)

# Uso:
# pdf_processado1 = enterPDF("exemplo_pdf_entrada.pdf")
# dados = pdf_processado1.process_enter()
# nome = pdf_processado1.get_company_name()