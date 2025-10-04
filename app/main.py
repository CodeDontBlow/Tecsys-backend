from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.db.chroma_db.manager import ChromaDBManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Test docker",
    description="branch = chore/embedding-ncm <docker>",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instância global do ChromaDBManager
chroma_manager = ChromaDBManager()

@app.get("/")
async def root():
    return {
        "message": "go to /docs",
    }


@app.get("/api/v1/search")
async def search_ncm(query: str):
    """
    - **query**: Termo de busca para componentes eletrônicos
    """
    try:
        if not query or len(query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query não pode estar vazia")
        
        logger.info(f"Buscando NCM para: {query}")
        result = chroma_manager.search_ncm(query)
        
        return {
            "success": True,
            "query": query,
            "results": [
                {
                    "ncm_code": item.ncm_code,
                    "description": item.description,
                    "distance": item.distance,
                    "is_parent": item.is_parent
                }
                for item in result.results
            ],
            "total_results": len(result.results)
        }
        
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno na busca: {str(e)}")

