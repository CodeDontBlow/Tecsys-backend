import asyncio
from app.services.extract_service.enterPDF import EnterPDF
from app.services.ollama_service.generate_final_desc import Generate_final_desc

async def generate_desc():
    # Processa o PDF
    pdf_processado1 = EnterPDF("exemplo_pdf_entrada.pdf")
    pdf_processado1.process_enter()

    erp_descs = pdf_processado1.get_erp_desc()
    supplyer_desc = ' test '

    test = ['02','03','04','05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15']
    for key in test:
        erp_descs.pop(key,None)
    print(erp_descs)
    print("""

    """)

    resultados_paralelo = await Generate_final_desc.generate_final_desc_async(erp_descs, supplyer_desc)
    
   
    return resultados_paralelo




descs = asyncio.run(generate_desc())
print(descs)