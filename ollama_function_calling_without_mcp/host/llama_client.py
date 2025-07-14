import requests
import json
from logger_config import logger

# 🌐 Endpoints
OLLAMA_API = "http://host.docker.internal:11434/api/chat"
APP_SERVER_URL = "http://app_server:8000"

# 🛠 Tool Schema (for Ollama function-calling)
tools = [
    {
        "name": "search_papers",
        "description": "Search for papers on arXiv based on a topic and store their information.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic to search for"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to retrieve",
                    "default": 5
                }
            },
            "required": ["topic"]
        }
    },
    {
        "name": "extract_info",
        "description": "Search for information about a specific paper across all topic directories.",
        "parameters": {
            "type": "object",
            "properties": {
                "paper_id": {
                    "type": "string",
                    "description": "The ID of the paper to look for"
                }
            },
            "required": ["paper_id"]
        }
    }
]

# 🧠 Tool Execution Logic — hits FastAPI backend
def search_papers(topic: str, max_results: int = 5):
    logger.info(f"Calling /search_papers with topic={topic}, max_results={max_results}")
    r = requests.get(f"{APP_SERVER_URL}/search_papers", params={"topic": topic, "max_results": max_results})
    r.raise_for_status()
    return r.json()

def extract_info(paper_id: str):
    logger.info(f"Calling /extract_info with paper_id={paper_id}")
    r = requests.get(f"{APP_SERVER_URL}/extract_info", params={"paper_id": paper_id})
    r.raise_for_status()
    return r.json()

mapping_tool_function = {
    "search_papers": search_papers,
    "extract_info": extract_info
}

def execute_tool(tool_name, tool_args):
    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
    try:
        result = mapping_tool_function[tool_name](**tool_args)

        if result is None:
            return "The operation completed but didn't return any results."

        elif isinstance(result, list):
            return ', '.join([str(r) for r in result])

        elif isinstance(result, dict):
            return json.dumps(result, indent=2)

        return str(result)

    except Exception as e:
        logger.exception(f"Tool execution failed for {tool_name}")
        return {"error": f"Execution failed: {str(e)}"}


# ✅ Check if Ollama is up
def ping_ollama():
    try:
        response = requests.get("http://host.docker.internal:11434/api/tags")
        is_up = response.status_code == 200
        logger.info(f"Ollama health check: {'✅ UP' if is_up else '❌ DOWN'}")
        return is_up
    except Exception as e:
        logger.exception("Failed to ping Ollama")
        return False


# 🧠 Main LLM send logic — with function_call capture
def send_to_ollama(messages):
    logger.info(f"Sending to Ollama. Last user message: {messages[-1]}")
    response = requests.post(
        OLLAMA_API,
        json={
            "model": "gemma:7b",
            "messages": messages,
            "functions": tools,
            "stream": True
        }
    )
    logger.info(f"Actual response from Ollama: {response}")

    full_message = {"role": "assistant", "content": ""}
    function_call = None

    for line in response.iter_lines():
        if line:
            chunk = json.loads(line.decode("utf-8"))
            logger.debug(f"Ollama stream chunk: {chunk}")

            if "message" in chunk:
                full_message["content"] += chunk["message"].get("content", "")

            if "function_call" in chunk:
                function_call = chunk["function_call"]

            if chunk.get("done"):
                break

    logger.info(f"Ollama final message: {full_message['content']}")
    result = {"message": full_message}
    if function_call:
        logger.info(f"Function call requested: {function_call}")
        result["function_call"] = function_call
    return result


# 🔁 Full query lifecycle
def process_query(query):
    logger.info(f"User query: {query}")
    system_message = {
        "role": "system",
        "content": (
            "You are a helpful AI assistant with access to tools."
            "Whenever a query can benefit from using a function (like searching papers or extracting info), "
            "you MUST call the appropriate function instead of answering directly."
            "Please compulsorily use the tools at your displosal and ensure you activate function call"
        )
    }
    history = [system_message] + [{"role": "user", "content": query}]
    response = send_to_ollama(history)

    if "function_call" in response:
        func = response["function_call"]
        logger.info(f"Function called: {func['name']} with args: {func['arguments']}")
        tool_result = execute_tool(func["name"], func["arguments"])
        history.append({"role": "function", "name": func["name"], "content": tool_result})

        final_response = send_to_ollama(history)
        logger.info(f"Final assistant message: {final_response['message']['content']}")
        print("\n🤖", final_response["message"]["content"])
    else:
        logger.info("No function call; direct LLM response.")
        print("\n🤖", response["message"]["content"])
