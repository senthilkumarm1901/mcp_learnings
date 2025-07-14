import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
from tools_client import tools_schema, search_papers, extract_info, system_prompt

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("API_VERSION")
)

deployment_name = os.getenv("MODEL_NAME")

def chatbot():
    messages = [{"role": "system", "content": system_prompt}]

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("👋 Chatbot: Goodbye! It was nice talking to you.")
            break

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
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

                print(f"🔧 Tool called: {tool_name} with args: {function_args}")

                # Call actual Python tool
                if tool_name == "search_papers":
                    tool_response = search_papers(**function_args)
                elif tool_name == "extract_info":
                    tool_response = extract_info(**function_args)
                else:
                    tool_response = {"error": "Unknown tool"}

                # Append the model's tool call
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call],
                })

                # Append the tool's result
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(tool_response),
                })

                # Follow-up request
                follow_up = client.chat.completions.create(
                    model=deployment_name,
                    messages=messages
                )
                final_msg = follow_up.choices[0].message
                print(f"🤖 Bot: {final_msg.content}\n")
                messages.append({"role": "assistant", "content": final_msg.content})

        else:
            print(f"🤖 Bot: {response_message.content}\n")
            messages.append({"role": "assistant", "content": response_message.content})


if __name__ == '__main__':
    chatbot()