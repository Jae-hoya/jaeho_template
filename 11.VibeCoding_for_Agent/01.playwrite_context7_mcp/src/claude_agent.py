import json
from typing import Any, Dict, List
from openai import OpenAI


SYSTEM_PROMPT = """You are an intelligent assistant with access to multiple MCP (Model Context Protocol) tools.

## Available Tool Categories

### 1. Playwright Tools (Web Automation)
You have access to various Playwright tools to automate browser interactions:
- Navigate to URLs
- Click elements
- Fill forms
- Take screenshots
- Execute JavaScript
- And more

### 2. Context7 Tools (Library Documentation)
You have access to Context7 tools for retrieving up-to-date library documentation:
- **resolve-library-id**: Find the correct library ID for a package/library name
- **get-library-docs**: Get documentation and code examples for a library

**Important**: When looking up library documentation:
1. First use `resolve-library-id` to find the correct library ID
2. Then use `get-library-docs` with the resolved ID to get documentation

## Guidelines

When a user asks you to perform tasks:
1. Identify whether the task requires web automation (Playwright) or documentation lookup (Context7)
2. Use the appropriate MCP tools available to you
3. Break down complex tasks into steps
4. Provide clear feedback about what you're doing
5. Handle errors gracefully

Always use the tools provided. Do not simulate or pretend to use tools."""


def convert_to_openai_tools(mcp_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert MCP tool format to OpenAI function calling format"""
    openai_tools = []
    for tool in mcp_tools:
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("input_schema", {"type": "object", "properties": {}})
            }
        }
        openai_tools.append(openai_tool)
    return openai_tools


class ClaudeAgent:
    """OpenAI Agent for processing user requests with MCP tools"""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.conversation_history: List[Dict[str, Any]] = []

    async def process_message(
        self,
        user_message: str,
        available_tools: List[Dict[str, Any]],
        tool_executor: Any
    ) -> str:
        """Process user message with OpenAI and execute tools"""

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Convert MCP tools to OpenAI format
        openai_tools = convert_to_openai_tools(available_tools)

        while True:
            # Build messages with system prompt
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.conversation_history

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=openai_tools if openai_tools else None,
                tool_choice="auto" if openai_tools else None
            )

            assistant_message = response.choices[0].message

            # Check if there are tool calls
            if assistant_message.tool_calls:
                # Add assistant response with tool calls to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute tools
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    print(f"\n[Tool Call] {tool_name}")
                    print(f"[Parameters] {json.dumps(tool_args, indent=2)}")

                    try:
                        result = await tool_executor(tool_name, tool_args)
                        tool_result = str(result)
                        print(f"[Result] Success")
                    except Exception as e:
                        tool_result = f"Error: {str(e)}"
                        print(f"[Result] Error: {str(e)}")

                    # Add tool result to history
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })

                # Continue conversation loop to get final response

            else:
                # No tool calls, return text response
                text_content = assistant_message.content or ""

                # Add assistant response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": text_content
                })

                return text_content

    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
