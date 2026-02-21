from dotenv import load_dotenv
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from typing import List
import asyncio
import nest_asyncio
import json

nest_asyncio.apply()

load_dotenv()

class MCP_ChatBot:

    def __init__(self):
        self.session: ClientSession = None
        self.openai_client = OpenAI()
        self.available_tools: List[dict] = []

    async def process_query(self, query):
        # Build dynamic system prompt based on available tools
        tool_info = "\n".join(
            f"- {t['function']['name']}: {t['function']['description']}"
            for t in self.available_tools
        )
        system_prompt = (
            "You are a research assistant. You have access to these tools:\n"
            f"{tool_info}\n"
            "When greeted, introduce yourself and your capabilities."
        )

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': query}
        ]

        response = self.openai_client.chat.completions.create(
            model='gpt-5.1',
            tools=self.available_tools,
            messages=messages
        )
        process_flag = True
        while process_flag:
            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            if finish_reason == 'stop' or not message.tool_calls:
                print(message.content)
                process_flag = False

            elif finish_reason == 'tool_calls':
                messages.append(message)
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    tool_call_id = tool_call.id

                    print(f"Calling tool {tool_name} with args {tool_args}")

                    # Tool invocation through the MCP client session
                    result = await self.session.call_tool(tool_name, arguments=tool_args)
                    result_text = "".join(
                        block.text for block in result.content
                        if hasattr(block, 'text')
                    )
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": result_text
                    })

                response = self.openai_client.chat.completions.create(
                    model='gpt-5.1',
                    tools=self.available_tools,
                    messages=messages
                )
                if response.choices[0].finish_reason == 'stop':
                    print(response.choices[0].message.content)
                    process_flag = False

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                await self.process_query(query)
                print("\n")
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def connect_to_server_and_run(self):
        server_params = StdioServerParameters(
            command="python",
            args=["research_server.py"],
            env=None,
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                await session.initialize()

                response = await session.list_tools()
                tools = response.tools
                print("\nConnected to server with tools:", [tool.name for tool in tools])

                # Convert MCP tool schema to OpenAI function-calling format
                self.available_tools = [{
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                } for tool in tools]

                await self.chat_loop()


async def main():
    chatbot = MCP_ChatBot()
    await chatbot.connect_to_server_and_run()


if __name__ == "__main__":
    asyncio.run(main())
