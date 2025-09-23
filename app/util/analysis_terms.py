from app.db.chroma_db.config import CSV_PATH
import re
from collections import Counter
import pandas as pd

def formated(text:str):
    stopwords = {"de", "a", "o", "os", "as", "em", "até", "com", "para", "e", "ou", "por", "na", "no"}

    text = re.sub(r"[^\w\s]", " ", text.lower()) #transistores exceto os fototransistores
    text_list = text.split() #["transistores" "exceto" "os" "fototransistores"]
    return [t for t in text_list if t not in stopwords] #["Transistores" "exceto" "fototransistores"]

def most_terms_repeated():
    csv:str = CSV_PATH
    
    df = pd.read_csv(csv)
    descriptions = df["Descricao"].dropna().tolist()

    counter = Counter()
    for d in descriptions:
        formated_text = formated(d)
        counter.update(formated_text) 

    most_common_terms = counter.most_common(1000)
    
    print("Terms most common:")
    for term, freq in most_common_terms:
        print(f"{term}: {freq}")