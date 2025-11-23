from app.db.chroma_db.manager import chroma_manager
from app.db.chroma_db.model import Response
from fastapi import HTTPException

async def get_ncm(query: str) -> dict:
    if not query or not query.strip():
        raise ValueError("Query cannot be empty!")
    
    try:
        response: Response = chroma_manager.search_ncm(query)
        if not response:
            raise HTTPException(status_code=404, detail="Not Found")
        
        ncms = []
        father = None
        childrens = []

        for r in response.results:
            item = {
                "ncm_code": r.ncm_code,
                "description": r.description,
                "aliquot": r.aliquot,
                "distance": r.distance
            }

            if r.is_parent:
                if father:
                    father["ncm_8"] = childrens
                    ncms.append(father)

                
                father = {
                    "ncm_6": r.ncm_code, 
                    "description": r.description,
                    "aliquot": r.aliquot,
                    "distance": r.distance
                }
                childrens = []
            else:
                childrens.append(item)

        if father:
            father["ncm_8"] = childrens
            ncms.append(father)

        return {
            "query_original": query,
            "ncms": ncms
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))