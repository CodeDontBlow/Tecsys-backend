from app.services.extract_service.extract_json import Extract_json
from app.services.extract_service.find_info import Find_info
from app.services.extract_service.pdf2txt import pdf_to_text

texto = pdf_to_text("exemplo_pdf_entrada.pdf")
data_json = Extract_json.return_Datajson(texto)

print(data_json)
print(Find_info.find_company_name(texto))

# add the EnterPDF method