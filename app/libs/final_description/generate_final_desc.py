# import asyncio, time
# from .clean_response import Clean_response
# from ollama import AsyncClient

# class Generate_final_desc:

#     @staticmethod
#     async def generate_final_desc_async(erp_desc, supplier_desc):
#         # print(f"Total descriptions to process:{len(erp_desc)}")
        
#         llm_description = 'descriptum:latest'

#         client = AsyncClient()
        
#         tasks = []
#         for i, (codigo, descricao) in enumerate(erp_desc.items(), 1):
#             # print(f"  {i}. Código: {codigo} - Descrição: {descricao[:50]} {supplier_desc}...")


#             task = client.generate(llm_description, descricao + ' ' + supplier_desc)

#             tasks.append(task)
        

#         start_time = time.time()
        

#         responses = await asyncio.gather(*tasks)
        

#         end_time = time.time()
#         print(f" req async complete")
#         print(f" total time: {end_time - start_time:.2f} secs")
        

#         resultados = {}

#         for (codigo, descricao), response in zip(erp_desc.items(), responses):
#             resposta_limpa = Clean_response.clean_response(response['response'])
#             resultados[codigo] = resposta_limpa
        
        

        
#         return resultados













import asyncio
from .clean_response import Clean_response


class Generate_final_desc:

    """Caso não queira utilizar o LLM localmente, use esta opção que retorna uma resposta fixa."""


    @staticmethod
    async def generate_final_desc_async(erp_desc, supplier_desc):
        """Retorna uma resposta fixa para cada item em `erp_desc`.

        Observação: opção temporária para máquinas que não conseguem executar
        o LLM localmente. Retorna a string limpa "Teste" para cada código.
        """

        resultados = {}
        for codigo in erp_desc.keys():
            resposta_limpa = Clean_response.clean_response("Teste")
            resultados[codigo] = resposta_limpa

        return resultados

