from app.db.chroma_db.manager import chroma_manager
from app.db.chroma_db.model import Response

def get_ncm(query: str) -> dict:
    if not query or not query.strip():
        raise ValueError("Query cannot be empty!")
    
    response: Response = chroma_manager.search_ncm(query)

    if not response.results:
        return None 

    return {
        "query original": query,
        "results": [
            {
                "ncm_code": r.ncm_code,
                "description": r.description,
                "distance": r.distance
            }
            for r in response.results
        ]
    }
