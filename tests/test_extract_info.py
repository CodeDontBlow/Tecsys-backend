from app.scripts.extract_json import Extract_json
from app.scripts.find_info import Find_info
from app.scripts.pdf2txt import pdf_to_text_native

texto = pdf_to_text_native("exemplo_pdf_entrada.pdf")
print(texto)
data_json = Extract_json.return_Datajson(texto)

print(data_json)
print(Find_info.find_company_name(texto))