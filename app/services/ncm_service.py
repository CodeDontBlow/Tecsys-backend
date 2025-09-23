from app.db.chroma_db.manager import chroma_manager
from app.db.chroma_db.model import Response

def get_ncm(query: str) -> Response:
    if not query or not query.strip():
        raise ValueError("Query cannot be empty!")
    
    response: Response = chroma_manager.search_ncm(query)

    if response.result is None:
        return None 
    
    return {
        "query original": query,
        "ncm_code": response.result.ncm_code,
        "description": response.result.description
    }
