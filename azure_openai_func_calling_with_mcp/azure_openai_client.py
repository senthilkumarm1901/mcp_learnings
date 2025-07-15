import os
import json
import asyncio
from dotenv import load_dotenv
from openai import AzureOpenAI

from logger_config import logger
from tools_client import system_prompt, tools_schema, search_papers, extract_info

from fastmcp import Client as MCPClient
from fastmcp.client.transports import StreamableHttpTransport

load_dotenv()

# Azure OpenAI Client
azure_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("API_VERSION")
)
deployment_name = os.getenv("MODEL_NAME")

# MCP Client
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")
mcp_transport = StreamableHttpTransport(url=MCP_SERVER_URL)
mcp_client = MCPClient(mcp_transport)


async def print_tools():
    async with mcp_client:
        await mcp_client.ping()
        tools = await mcp_client.list_tools()
        print("🧰 Available Tools:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description.strip() if tool.description else 'No description'}")



async def print_prompts():
    async with mcp_client:
        await mcp_client.ping()
        prompts = await mcp_client.list_prompts()
        print("🧠 Available Prompts:")
        for prompt in prompts:
            print(f"🔹 {prompt.name}")
            if prompt.description:
                print(f"   {prompt.description.strip()}")
            if prompt.arguments:
                print("   Arguments:")
                for arg in prompt.arguments:
                    print(f"     - {arg.name}" + (" (required)" if arg.required else " (optional)"))


def chatbot():
    logger.info("🔁 Chatbot session started.")
    messages = [{"role": "system", "content": system_prompt}]

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("👋 Chatbot: Goodbye! It was nice talking to you.")
            logger.info("👋 User exited chat session.")
            break

        # Handle /tools command
        if user_input == "/tools":
            asyncio.run(print_tools())
            continue

        # Handle /prompts command
        if user_input == "/prompts":
            asyncio.run(print_prompts())
            continue

        logger.info(f"📥 User input: {user_input}")
        messages.append({"role": "user", "content": user_input})

        response = azure_client.chat.completions.create(
            model=deployment_name,
            messages=messages,
            tools=tools_schema,
            tool_choice="auto"
        )

        response_message = response.choices[0].message

        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                logger.info(f"🛠️ Tool called: {tool_name} with args: {function_args}")
                print(f"🔧 Tool called: {tool_name} with args: {function_args}")

                try:
                    if tool_name == "search_papers":
                        tool_response = search_papers(**function_args)
                    elif tool_name == "extract_info":
                        tool_response = extract_info(**function_args)
                    else:
                        tool_response = {"error": "Unknown tool"}
                except Exception as e:
                    logger.exception(f"❌ MCP tool call failed: {e}")
                    tool_response = {"error": str(e)}

                logger.info(f"📤 Tool response: {tool_response}")

                # Add assistant tool call + tool result
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call],
                })

                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": str(tool_response),
                })

                # Now let the model continue
                follow_up = azure_client.chat.completions.create(
                    model=deployment_name,
                    messages=messages
                )
                final_msg = follow_up.choices[0].message
                print(f"🤖 Bot: {final_msg.content}\n")
                logger.info(f"🤖 Final bot message: {final_msg.content}")
                messages.append({"role": "assistant", "content": final_msg.content})

        else:
            print(f"🤖 Bot: {response_message.content}\n")
            logger.info(f"🤖 Bot message (no tool): {response_message.content}")
            messages.append({"role": "assistant", "content": response_message.content})


if __name__ == '__main__':
    chatbot()