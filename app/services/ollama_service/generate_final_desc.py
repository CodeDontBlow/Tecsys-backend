import os
import json
from ollama import generate
from dotenv import load_dotenv

class Generate_final_desc:
    load_dotenv()
    
    def get_product_json():
        

        return []





    

    def generate_final_desc(desc_erp, desc_supplyer):
        llm_description = os.getenv("LLM_DESCRIPTION")
        


        response = generate(llm_description, 'RES.SMD 0603 20K 1% 1/10W')
        # print(response['response'])
        return 
