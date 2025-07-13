import requests
import json

# if streaming chat logs
# import sseclient

OLLAMA_API = "http://host.docker.internal:11434/api/chat"
APP_SERVER_URL = "http://app_server:8000"

def ping_ollama():
    try:
        response = requests.get("http://host.docker.internal:11434/api/tags")
        return response.status_code == 200
    except Exception as e:
        print("Error connecting to Ollama:", e)
        return False


def handle_function_call(name, arguments):
    if name == "arxiv_search":
        q = arguments.get("q", "")
        # You can change this to /arxiv/stream if using SSE
        response = requests.get(f"{APP_SERVER_URL}/arxiv", params={"q": q})
        return response.json()
    return {"error": "Unknown function."}


def send_to_ollama(messages):
    response = requests.post(
        OLLAMA_API,
        json={"model": "gemma:7b", "messages": messages},
        stream=True
    )

    full_message = {"role": "assistant", "content": ""}
    function_call = None

    for line in response.iter_lines():
        if line:
            chunk = json.loads(line.decode("utf-8"))

            if "message" in chunk:
                role = chunk["message"].get("role")
                content = chunk["message"].get("content", "")
                full_message["content"] += content

            if "function_call" in chunk:
                function_call = chunk["function_call"]

            if chunk.get("done"):
                break

    result = {"message": full_message}
    if function_call:
        result["function_call"] = function_call
    return result


def process_query(query):
    history = [{"role": "user", "content": query}]
    response = send_to_ollama(history)

    # Function calling detected
    if "function_call" in response:
        func = response["function_call"]
        print(f"\n[🔧 Tool Call] {func['name']} with args {func['arguments']}")
        tool_result = handle_function_call(func["name"], func["arguments"])

        # Send tool result back to LLM
        history.append({"role": "function", "name": func["name"], "content": str(tool_result)})
        final_response = send_to_ollama(history)
        print("\n🤖", final_response["message"]["content"])
    else:
        print("\n🤖", response["message"]["content"])