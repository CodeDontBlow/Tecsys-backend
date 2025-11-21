import json

from .pdf2txt import pdf_to_text
from .extract_json import Extract_json
from .find_info import Find_info


class EnterPDF:
    def __init__(self, bytes_pdf):
        self.bytes_pdf = bytes_pdf
        self.text = None
        self.data = None

    def process_enter(self):
        """principal method enter(to extract)"""
        self.text = pdf_to_text(self.bytes_pdf)
        self.data = json.loads(Extract_json.return_Datajson(self.text))

        return self.data

    def get_supplier_name(self):
        return Find_info.find_supplier_name(self.text)

    def get_erp_desc(self, data: dict):
        desc = {
            product["number"]: product["name"]
            for product in data.values()
        }
        return desc

    def get_pn(self):
        pn = {
            product["number"]: product["part_number"]
            for product in self.data.values()
        }
        return pn

    def get_erp_code(self):
        code = {
            product["number"]: product["erp_code"]
            for product in self.data.values()
        }
        return code
