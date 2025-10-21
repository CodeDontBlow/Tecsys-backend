from app.db.chroma_db.manager import chroma_manager
from app.db.chroma_db.model import Response
from fastapi import HTTPException

def get_ncm(query: str) -> dict:
    if not query or not query.strip():
        raise ValueError("Query cannot be empty!")
    try:
        response: Response = chroma_manager.search_ncm(query)
        if not response:
            raise HTTPException(status_code=404, detail="Not Found")
        return {
            "query original": query,
            "results": [
                {
                    "ncm_code": r.ncm_code,
                    "description": r.description,
                    "distance": r.distance,
                    "aliquot": r.aliquot,
                    "is_parent": r.is_parent
                }
                for r in response.results
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))