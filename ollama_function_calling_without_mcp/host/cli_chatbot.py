from llama_client import send_to_ollama, handle_function_call, ping_ollama

# 🧪 Check if Ollama server is running
if not ping_ollama():
    print("❌ Ollama server not reachable. Please start it with:\n\n    ollama run gemma:7b\n")
    exit(1)

print("💬 Chat started. Type 'exit' or 'quit' to stop.\n")



history = []

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in {"exit", "quit"}:
        print("👋 Exiting chat. Goodbye!")
        break
    history.append({"role": "user", "content": user_input})
    response = send_to_ollama(history)

    if 'function_call' in response:
        func = response['function_call']
        tool_result = handle_function_call(func['name'], func['arguments'])
        history.append({"role": "function", "name": func["name"], "content": str(tool_result)})
        final = send_to_ollama(history)
        print("Bot:", final["message"]["content"])
        history.append(final["message"])
    else:
        print("Bot:", response["message"]["content"])
        history.append(response["message"])
