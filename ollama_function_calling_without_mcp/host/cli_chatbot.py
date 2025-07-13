from llama_client import process_query, ping_ollama

def chat_loop():
    print("💬 Chat started. Type 'quit' or 'exit' to stop.\n")
    while True:
        try:
            query = input("You: ").strip()
            if query.lower() in {"quit", "exit"}:
                print("👋 Exiting chat.")
                break
            process_query(query)
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    if not ping_ollama():
        print("❌ Ollama server not reachable. Please start it with:\n\n    ollama run gemma:7b\n")
        exit(1)
    chat_loop()