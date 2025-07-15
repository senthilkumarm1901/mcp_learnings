uv init -p 3.10
uv venv
source .venv/bin/activate
uv add arxiv "fastmcp[cli]" openai

# to run the server
uv run app_server.py

```
INFO:     Started server process [56490]
INFO:     Waiting for application startup.
[07/14/25 22:07:42] INFO     StreamableHTTP session manager started                                                                                                                     streamable_http_manager.py:111
INFO:     Application startup complete.

...
...
INFO     Processing request of type CallToolRequest                                                                                                                                  server.py:625
INFO     Requesting page (first: True, try: 0): https://export.arxiv.org/api/query?search_query=Agentic+RAG&id_list=&sortBy=relevance&sortOrder=descending&start=0&max_results=100 __init__.py:680
[07/14/25 22:09:31] INFO     Got first page: 100 of 50781 total results                                                                                                                                __init__.py:606
Results are saved in: papers/agentic_rag/papers_info.json
```

# to run the client
uv run azure_openai_client.py

```
You: Can you search papers on Agentic RAG?
🔧 Tool called: search_papers with args: {'topic': 'Agentic RAG', 'max_results': 5}
🤖 Bot: I found several research papers related to the topic of "Agentic RAG." Here are some papers you might find interesting:

1. **Paper ID: 2501.09136v3**
2. **Paper ID: 2410.13509v2**
3. **Paper ID: 2501.15228v1**
4. **Paper ID: 2504.10147v1**
5. **Paper ID: 2506.10408v1**

If you would like to get detailed information or summaries for any of these papers, please let me know which one(s) you're interested in!

You: 2501.09136v3
🔧 Tool called: extract_info with args: {'paper_id': '2501.09136v3'}
🤖 Bot: Here are the details of the paper titled **"Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG"**:

- **Authors**: Aditi Singh, Abul Ehtesham, Saket Kumar, Tala Talaei Khoei
- **Published**: January 15, 2025
- **Summary**: 
    - Large Language Models (LLMs) have transformed artificial intelligence (AI) by enhancing human-like text generation and natural language comprehension. However, their dependency on static training data restricts their ability to answer dynamic, real-time inquiries, leading to potentially outdated or inaccurate outputs. 
    - Retrieval-Augmented Generation (RAG) has emerged as a solution by integrating real-time data retrieval to produce contextually relevant and up-to-date responses. Still, traditional RAG systems are impeded by static workflows and lack the adaptability necessary for multistep reasoning and complex task management.
    - Agentic Retrieval-Augmented Generation (Agentic RAG) surpasses these restrictions by incorporating autonomous AI agents into the RAG pipeline. These agents utilize various design patterns—such as reflection, planning, tool use, and multiagent collaboration—to dynamically manage retrieval strategies, refine contextual understanding iteratively, and adapt workflows to accommodate complex task requirements. This integration allows Agentic RAG systems to provide exceptional flexibility, scalability, and context awareness across various applications.
    - This survey explores Agentic RAG's foundational principles and the evolution of RAG paradigms, providing a thorough taxonomy of its architectures. It discusses key applications in sectors like healthcare, finance, and education while examining practical implementation strategies. It also addresses challenges in scaling these systems, ensuring ethical decision-making, and optimizing performance for real-world applications, offering insights into frameworks and tools suitable for implementing Agentic RAG.

- **PDF Link**: [Download the paper](http://arxiv.org/pdf/2501.09136v3)

If you need further information or have any specific questions about this paper, feel free to ask!
```