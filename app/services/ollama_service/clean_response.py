import re
class Clean_response:

    @staticmethod
    def _clean_response(response_text):
       cleaned_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
       cleaned_text = re.sub(r'<think>.*', '', cleaned_text, flags=re.DOTALL)
       cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text.strip())
        
       return cleaned_text.strip()