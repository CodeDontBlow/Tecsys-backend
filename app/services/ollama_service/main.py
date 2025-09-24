import asyncio
from app.services.extract_service.enterPDF import EnterPDF
from app.services.ollama_service.generate_final_desc import Generate_final_desc

async def main():
    # Processa o PDF
    pdf_processado1 = EnterPDF("exemplo_pdf_entrada.pdf")
    dados = pdf_processado1.process_enter()
    descs = pdf_processado1.get_erp_desc()
    
    # Gera descrições finais (em paralelo)
    resultados_paralelo = await Generate_final_desc.generate_final_desc_async(descs)
    
    # Ou sequencialmente 
    # resultados_sequencial = await Generate_final_desc.generate_final_desc_sequential(descs)
    
    print("Resultados:", resultados_paralelo)

# Para executar
if __name__ == "__main__":
    asyncio.run(main())