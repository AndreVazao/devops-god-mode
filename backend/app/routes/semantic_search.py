from fastapi import APIRouter
from pydantic import BaseModel
from app.services.semantic_search import search_code
from app.services.semantic_index_builder import build_index

router = APIRouter(prefix="/api/semantic-search", tags=["semantic-search"])

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/query")
async def query_code(request: SearchRequest):
    results = search_code(request.query, request.top_k)
    return {"results": results}

@router.post("/rebuild")
async def trigger_rebuild():
    res = build_index()
    return res
