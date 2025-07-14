import os
import json
import arxiv
from typing import List

PAPER_DIR = "./paper_data"  # Can be configured as needed


def get_paper_info_path(topic: str) -> str:
    path = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, "papers_info.json")


def load_existing_papers(file_path: str) -> dict:
    try:
        with open(file_path, "r") as json_file:
            return json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_papers(file_path: str, papers_info: dict):
    with open(file_path, "w") as json_file:
        json.dump(papers_info, json_file, indent=2)


def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic and store their information.
    """
    client = arxiv.Client()
    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    results = client.results(search)

    file_path = get_paper_info_path(topic)
    papers_info = load_existing_papers(file_path)
    paper_ids = []

    for paper in results:
        paper_id = paper.get_short_id()
        paper_ids.append(paper_id)
        papers_info[paper_id] = {
            'title': paper.title,
            'authors': [author.name for author in paper.authors],
            'summary': paper.summary,
            'pdf_url': paper.pdf_url,
            'published': str(paper.published.date())
        }

    save_papers(file_path, papers_info)
    return paper_ids


def extract_info(paper_id: str) -> dict:
    """
    Search for information about a specific paper across all topic directories.
    """
    for item in os.listdir(PAPER_DIR):
        topic_dir = os.path.join(PAPER_DIR, item)
        if os.path.isdir(topic_dir):
            file_path = os.path.join(topic_dir, "papers_info.json")
            try:
                papers_info = load_existing_papers(file_path)
                if paper_id in papers_info:
                    return papers_info[paper_id]
            except Exception:
                continue

    return {"error": f"No saved information found for paper ID: {paper_id}"}
