import os
import json
import requests

PAPER_SERVER_API = os.getenv("PAPER_SERVER_API", "http://app_server:8001")

system_prompt = (
    "You are a helpful assistant who can search academic papers using the 'search_papers' tool, "
    "and provide detailed info using 'extract_info'. Always use a tool when it's helpful."
)

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "search_papers",
            "description": "Search for papers on arXiv based on a topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to search papers for"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Max number of papers to return",
                        "default": 5
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_info",
            "description": "Get info about a specific paper by its arXiv ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_id": {
                        "type": "string",
                        "description": "The arXiv ID of the paper"
                    }
                },
                "required": ["paper_id"]
            }
        }
    }
]

def search_papers(topic: str, max_results: int = 5):
    try:
        response = requests.get(f"{PAPER_SERVER_API}/search_papers", params={"topic": topic, "max_results": max_results})
        return response.json()
    except Exception as e:
        return {"error": f"Failed to call search_papers API: {str(e)}"}

def extract_info(paper_id: str):
    try:
        response = requests.get(f"{PAPER_SERVER_API}/extract_info", params={"paper_id": paper_id})
        return response.json()
    except Exception as e:
        return {"error": f"Failed to call extract_info API: {str(e)}"}