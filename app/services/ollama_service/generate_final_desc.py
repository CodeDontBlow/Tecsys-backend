import os
import asyncio
import time
import re
from app.services.extract_service.enterPDF import EnterPDF
from ollama import AsyncClient  # Use o cliente assíncrono
from dotenv import load_dotenv

class Generate_final_desc:
    load_dotenv()

    @staticmethod
    def _clean_response(response_text):
       """Remove tags <think> e qualquer conteúdo entre elas"""
       # Remove conteúdo entre <think> e </think>
       cleaned_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
        
        # Remove qualquer tag <think> solta (caso não tenha fechamento)
       cleaned_text = re.sub(r'<think>.*', '', cleaned_text, flags=re.DOTALL)
        
        # Remove espaços em excesso e quebras de linha extras
       cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text.strip())
        
       return cleaned_text.strip()


    @staticmethod
    async def generate_final_desc_async(descs):
        print(f"Total descriptions to process:{len(descs)}")
        
        llm_description = os.getenv("LLM_DESC")
        print(f" llm configred: {'yes' if llm_description else 'no'}")
        
        client = AsyncClient()
        

        tasks = []
        print("\n cooking tasks:")
        for i, (codigo, descricao) in enumerate(descs.items(), 1):
            print(f"  {i}. Código: {codigo} - Descrição: {descricao[:50]}...")
            task = client.generate(llm_description, descricao)
            tasks.append(task)
        
        print(f"\n send {len(tasks)} req async...")
        start_time = time.time()
        
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        print(f" req async complete")
        print(f" total time: {end_time - start_time:.2f} secs")
        

        resultados = {}
        print("\n process results:")
        for (codigo, descricao), response in zip(descs.items(), responses):
            # remove os thinks
            resposta_limpa = Generate_final_desc._clean_response(response['response'])
            resultados[codigo] = resposta_limpa
            
            print(f"  ✓ Código {codigo}")
            print(f"    original response: {len(response['response'])} caracteres")
            print(f"    cleaned response: {len(resposta_limpa)} caracteres")
            if len(resposta_limpa) < len(response['response']):
                print(f"      removed: {len(response['response']) - len(resposta_limpa)} caracteres")
        
        
        print(f"\n process finished")
        print(f" total of descs: {len(resultados)}")
        
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