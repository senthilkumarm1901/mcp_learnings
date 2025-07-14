from fastapi import FastAPI, Query
from tools import search_papers, extract_info
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/search_papers")
def search_papers_endpoint(topic: str = Query(...), max_results: int = 5):
    """
    Endpoint to search for papers and store them.
    Returns a list of paper IDs.
    """
    logger.info(f"🔍 Searching papers for topic: {topic}")
    return search_papers(topic, max_results)


@app.get("/extract_info")
def extract_info_endpoint(paper_id: str = Query(...)):
    """
    Endpoint to extract info about a paper.
    Returns the full metadata if found.
    """
    logger.info(f"📄 Extracting info for paper_id: {paper_id}")
    return extract_info(paper_id)


@app.get("/health")
def health_check():
    return {"status": "ok"}
