from app.util.table_ncm import fetch_ncm_data
from app.db.chroma_db.manager import chroma_manager

fetch_ncm_data() #Baixa csv 
chroma_manager.populate_from_csv() #Popula o banco de dados vetorizado

 