from app.scripts.extract import company_name, return_Datajson
from app.scripts.pdf2txt import pdf_to_text_native

texto = pdf_to_text_native("exemplo_pdf_entrada.pdf")
print(texto)
data_json = return_Datajson(texto)

print(data_json)
print(company_name(texto))