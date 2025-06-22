from fastapi import FastAPI, Query
from tools import search_arxiv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/arxiv")
def arxiv_search(q: str = Query(...), max_results: int = 5):
    return search_arxiv(q, max_results)


@app.get("/health")
def health_check():
    return {"status": "ok"}