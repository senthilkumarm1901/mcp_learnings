import requests
import json

OLLAMA_API = "http://host.docker.internal:11434/api/chat"

# def send_to_ollama(messages):
#     response = requests.post(OLLAMA_API, json={"model": "gemma:7b", "messages": messages})
#     return response.json()

def send_to_ollama(messages):
    response = requests.post(
        "http://host.docker.internal:11434/api/chat",
        json={"model": "gemma:7b", "messages": messages},
        stream=True  # <-- key change
    )

    full_message = {"role": "assistant", "content": ""}
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line.decode("utf-8"))
            if "message" in chunk:
                full_message["content"] += chunk["message"].get("content", "")
            if chunk.get("done"):
                break

    return {"message": full_message}


def handle_function_call(name, arguments):
    if name == "arxiv_search":
        q = arguments.get("q")
        r = requests.get("http://app_server:8000/arxiv", params={"q": q})
        return r.json()
    return {"error": "Unknown function"}


def ping_ollama():
    try:
        response = requests.get("http://host.docker.internal:11434/api/tags")
        return response.status_code == 200
    except Exception as e:
        print("Error connecting to Ollama:", e)
        return False