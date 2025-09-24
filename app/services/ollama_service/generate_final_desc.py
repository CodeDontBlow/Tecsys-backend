import os
import asyncio
import time
from app.services.extract_service.enterPDF import EnterPDF
from ollama import AsyncClient  # Use o cliente assíncrono
from dotenv import load_dotenv

class Generate_final_desc:
    load_dotenv()

    @staticmethod
    async def generate_final_desc_async(descs):
        print(f" INICIANDO PROCESSO ASSÍNCRONO")
        print(f" Total de descrições para processar: {len(descs)}")
        
        llm_description = os.getenv("LLM_DESC")
        print(f" LLM configurado: {'Sim' if llm_description else 'Não'}")
        
        client = AsyncClient()
        

        tasks = []
        print("\n PREPARANDO TAREFAS:")
        for i, (codigo, descricao) in enumerate(descs.items(), 1):
            print(f"  {i}. Código: {codigo} - Descrição: {descricao[:50]}...")
            task = client.generate(llm_description, descricao)
            tasks.append(task)
        
        print(f"\n ENVIANDO {len(tasks)} REQUISIÇÕES ASSÍNCRONAS...")
        start_time = time.time()
        
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        print(f" TODAS AS REQUISIÇÕES CONCLUÍDAS!")
        print(f" Tempo total: {end_time - start_time:.2f} segundos")
        

        resultados = {}
        print("\n PROCESSANDO RESULTADOS:")
        for (codigo, descricao), response in zip(descs.items(), responses):
            resultados[codigo] = response['response']
            print(f"  ✓ Código {codigo} - Resposta: {len(response['response'])} caracteres")
        
        print(f"\n PROCESSO FINALIZADO COM SUCESSO!")
        print(f" Total de resultados gerados: {len(resultados)}")
        
        return resultados

















    # @staticmethod
    # async def generate_final_desc_async(descs):
    #     llm_description = os.getenv("LLM_DESC")
    #     client = AsyncClient()
        
    #     tasks = []
    #     for i, (codigo, descricao) in enumerate(descs.items(), 1):
    #         task = client.generate(llm_description, descricao)
    #         tasks.append(task)
        
    #     responses = await asyncio.gather(*tasks)
        
    #     resultados = {}
    #     for (codigo, descricao), response in zip(descs.items(), responses):
    #         resultados[codigo] = response['response']
        
    #     return resultados