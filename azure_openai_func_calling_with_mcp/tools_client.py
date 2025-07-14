import os
import json
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from logger_config import logger

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")

# Setup MCP client with Streamable HTTP transport
transport = StreamableHttpTransport(url=MCP_SERVER_URL)
client = Client(transport)

def call_mcp_tool(tool_name: str, args: dict):
    async def run_call():
        async with client:
            await client.ping()
            logger.info(f"Calling MCP tool: {tool_name} with args {args}")
            result = await client.call_tool(tool_name, args)
            logger.info(f"Tool result: {result}")
            return result
    import asyncio
    return asyncio.run(run_call())

def search_papers(topic: str, max_results: int = 5):
    return call_mcp_tool("search_papers", {"topic": topic, "max_results": max_results})

def extract_info(paper_id: str):
    return call_mcp_tool("extract_info", {"paper_id": paper_id})


# Define tool schema to match LLM expectations
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "search_papers",
            "description": "Search for academic papers using arXiv",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Research topic to search"},
                    "max_results": {"type": "integer", "description": "Number of papers to return"}
                },
                "required": ["topic"]
            }
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract_info",
            "description": "Extract metadata and summary of a paper using its ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_id": {"type": "string", "description": "ID of the paper"}
                },
                "required": ["paper_id"]
            }
        },
    }
]

# System prompt
system_prompt = (
    "You are an academic research assistant that can search for research papers and summarize them "
    "using available tools. Use `search_papers` to find papers and `extract_info` to get detailed info."
)