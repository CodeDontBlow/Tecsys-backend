import asyncio, time, re
import requests
from .llm_settings import Llm_settings
from .clean_response import Clean_response
from ollama import AsyncClient

class Generate_final_desc:

    @staticmethod
    async def generate_final_desc_async(erp_desc, supplyer_desc):
        print(f"Total descriptions to process:{len(erp_desc)}")
        
        llm_description = 'descriptum:latest'

        if not Llm_settings.check_model_exists(llm_description):
            Llm_settings.create_ollama_model()

        client = AsyncClient()
        
        tasks = []
        for i, (codigo, descricao) in enumerate(erp_desc.items(), 1):
            print(f"  {i}. Código: {codigo} - Descrição: {descricao[:50]} {supplyer_desc}...")


            task = client.generate(llm_description, descricao + ' ' + supplyer_desc)

            tasks.append(task)
        
        print(f"\n send {len(tasks)} req async...")
        start_time = time.time()
        

        responses = await asyncio.gather(*tasks)
        

        end_time = time.time()
        print(f" req async complete")
        print(f" total time: {end_time - start_time:.2f} secs")
        

        resultados = {}
        print("\n process results:")
        for (codigo, descricao), response in zip(erp_desc.items(), responses):
            resposta_limpa = Clean_response.clean_response(response['response'])
            resultados[codigo] = resposta_limpa
        
        
        print(f"\n process finished")
        
        return resultados













