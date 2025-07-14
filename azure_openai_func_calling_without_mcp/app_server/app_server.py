from fastapi import FastAPI, Query
from tools import search_papers, extract_info
from logger_config import logger

app = FastAPI()


@app.get("/search_papers")
def search_papers_endpoint(topic: str = Query(...), max_results: int = 5):
    """
    Endpoint to search for papers and store them.
    Returns a list of paper IDs.
    """
    logger.info(f"🔍 Endpoint hit: /search_papers with topic='{topic}', max_results={max_results}")
    try:
        result = search_papers(topic, max_results)
        logger.info(f"✅ Search complete. Found paper IDs: {result}")
        return result
    except Exception as e:
        logger.exception(f"❌ Error in search_papers: {e}")
        return {"error": str(e)}


@app.get("/extract_info")
def extract_info_endpoint(paper_id: str = Query(...)):
    """
    Endpoint to extract info about a paper.
    Returns the full metadata if found.
    """
    logger.info(f"📄 Endpoint hit: /extract_info with paper_id='{paper_id}'")
    try:
        result = extract_info(paper_id)
        logger.info(f"✅ Extraction result: {result}")
        return result
    except Exception as e:
        logger.exception(f"❌ Error in extract_info: {e}")
        return {"error": str(e)}


@app.get("/health")
def health_check():
    logger.info("❤️ Health check ping received.")
    return {"status": "ok"}