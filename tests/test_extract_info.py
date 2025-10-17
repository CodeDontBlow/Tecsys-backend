from app.services.extract_service.enterPDF import EnterPDF

# add the EnterPDF method

pdf_processado1 = EnterPDF("Pedido compras_Mouser.pdf")

dados = pdf_processado1.process_enter()
nome = pdf_processado1.get_supplier_name()

descs = pdf_processado1.get_erp_desc()
pns = pdf_processado1.get_pn()
codes = pdf_processado1.get_erp_code()


print(nome)
print("-" * 50)
print(descs)
print("-" * 50)
print(pns)
print("-" * 50)
print(codes)
print("-" * 50)
