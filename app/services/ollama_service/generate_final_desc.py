import os
import asyncio
from app.services.extract_service.enterPDF import EnterPDF
from ollama import AsyncClient  # Use o cliente assíncrono
from dotenv import load_dotenv

class Generate_final_desc:
    load_dotenv()
    
    @staticmethod
    async def generate_final_desc_async(descs):
        llm_description = os.getenv("LLM_DESCRIPTION")
        client = AsyncClient()
        
        tasks = []
        for i, (codigo, descricao) in enumerate(descs.items(), 1):
            task = client.generate(llm_description, descricao)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        resultados = {}
        for (codigo, descricao), response in zip(descs.items(), responses):
            resultados[codigo] = response['response']
        
        return resultados
    
    # @staticmethod
    # async def generate_final_desc_sequential(descs):
    #     """Versão assíncrona que processa sequencialmente (mais conservadora)"""
    #     llm_description = os.getenv("LLM_DESCRIPTION")
    #     client = AsyncClient()
        
    #     resultados = {}
    #     for i, (codigo, descricao) in enumerate(descs.items(), 1):
    #         response = await client.generate(llm_description, descricao)
    #         resultados[codigo] = response['response']
        
    #     return resultados

