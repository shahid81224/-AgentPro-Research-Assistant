"""Defines the ReAct Agent that orchestrates the tools."""

from tools.base_tool import Tool, LLMTool
from tools.search_tool import InternetSearchTool # We need the class for description
from tools.report_tool import ReportWritingTool
import re
import json
from typing import List, Dict, Any
from pydantic import Field

# Helper function to extract structured data (like JSON) from LLM response
def extract_json_block(text: str) -> Dict[str, Any] | None:
    """Extracts JSON data from a string.
    
    Tries to parse the entire string first, assuming response_format worked.
    Falls back to searching for a ```json ... ``` block if direct parsing fails.
    """
    try:
        # Attempt 1: Parse the entire string as JSON
        data = json.loads(text)
        print("Successfully parsed entire response as JSON.")
        return data
    except json.JSONDecodeError:
        print("Could not parse entire response as JSON, searching for ```json block...")
        # Attempt 2: Search for ```json block using regex
        match = re.search(r"```json\\n(.*?)\\n```", text, re.DOTALL | re.IGNORECASE) # Added IGNORECASE
        if match:
            json_str = match.group(1).strip()
            try:
                data = json.loads(json_str)
                print("Successfully parsed JSON block using regex.")
                return data
            except json.JSONDecodeError as e_inner:
                print(f"Error: Could not decode JSON from regex block: {json_str}. Error: {e_inner}")
                return None
        else:
            print("Error: No ```json block found using regex.")
            return None

class ReActAgent(LLMTool):
    """A ReAct (Reasoning and Acting) agent.

    This agent uses an LLM to reason about a task, choose appropriate tools,
    execute them, observe the results, and iterate until the task is complete.
    """
    tools: Dict[str, Tool] = Field(default_factory=dict, description="Dictionary of available tools keyed by name.")
    max_iterations: int = Field(5, description="Maximum number of ReAct iterations to prevent infinite loops.")

    # Override the base tool fields for the agent itself
    name: str = Field("ReAct Research Agent", description="The name of the agent.")
    description: str = Field(
        "Manages a research task by reasoning, searching the internet, and writing reports.",
        description="A detailed description of what the agent does."
    )
    arg_description: str = Field(
        "The overall research task or question.",
        description="Description of the expected input argument for the agent's run method."
    )

    def __init__(self, tools: List[Tool], **data):
        """Initializes the ReActAgent.

        Args:
            tools: A list of Tool instances available to the agent.
            **data: Additional Pydantic model data.
        """
        super().__init__(**data)
        self.tools = {tool.name: tool for tool in tools}
        if not self.client:
            raise ValueError("Agent requires an OpenAI client. Check API key.")

    def _get_system_prompt(self) -> str:
        """Creates the system prompt for the LLM, including tool descriptions."""
        tool_descriptions = "\n\n".join(
            [tool.get_tool_description_for_llm() for tool in self.tools.values()]
        )

        return f"""
You are a helpful research assistant operating in a ReAct (Reasoning + Acting) loop.
Your goal is to complete the user's task by breaking it down into steps.
At each step, you must first **Reason** about the current situation and the overall goal.
Then, based on your reasoning, you must decide on an **Action**. 

Available Actions:
1.  Choose one of the available tools to gather information or process data.
2.  Conclude the task if you have enough information and have fulfilled the user's request.

Available Tools:
{tool_descriptions}

Output Format:
You MUST structure your response as a JSON block like this:
```json
{{
  "thought": "<Your step-by-step reasoning process here. Explain why you are choosing a specific action.>",
  "action": {{
    "tool_name": "<Name of the tool to use (e.g., internet_search_tool) OR 'final_answer'>",
    "argument": "<The argument to pass to the tool, OR the final answer/report if action is 'final_answer'>"
  }}
}}
```

- If you choose a tool, provide its exact name in `tool_name` and the necessary input in `argument`.
- If you believe the task is complete, set `tool_name` to `final_answer` and provide the final response in `argument`.
- Do NOT just provide the final answer directly without the JSON structure.
- Stick to the available tools. Do not invent tools.
Begin!
"""

    def run(self, task: str) -> str:
        """Executes the ReAct loop to accomplish the given task.

        Args:
            task: The user's research task or question.

        Returns:
            The final result or report, or an error message.
        """
        if not self.client:
            return "Error: Agent cannot run without an OpenAI client."

        system_prompt = self._get_system_prompt()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"The user's task is: {task}"}
        ]

        print(f"--- Starting ReAct Loop for Task: {task} ---")

        for i in range(self.max_iterations):
            print(f"\n--- Iteration {i + 1} ---")
            print(f"Current Messages: {json.dumps(messages, indent=2)}")

            try:
                # --- Reasoning Step ---                
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=0.7,
                    response_format={"type": "json_object"} # Request JSON output if supported
                )
                llm_output = response.choices[0].message.content
                print(f"LLM Response:\n{llm_output}")
                messages.append({"role": "assistant", "content": llm_output})

                # --- Parse Action ---                
                action_data = extract_json_block(llm_output)
                if not action_data or 'action' not in action_data or 'tool_name' not in action_data['action']:
                    print("Error: Could not parse valid action from LLM response.")
                    # Add observation about parsing failure
                    messages.append({"role": "user", "content": "Observation: Your previous response was not in the expected JSON format. Please think step-by-step and provide your reasoning and action in the specified JSON structure."})                    
                    continue # Try again in the next iteration

                thought = action_data.get('thought', 'No thought provided.')
                tool_name = action_data['action'].get('tool_name')
                argument = action_data['action'].get('argument')

                print(f"Thought: {thought}")
                print(f"Action: Tool={tool_name}, Argument={argument[:100]}...") # Truncate long args

                # --- Action Step ---                
                if tool_name == "final_answer":
                    print("--- ReAct Loop Finished: Final Answer Provided --- ")
                    return argument # Task complete

                if tool_name not in self.tools:
                    observation = f"Error: Tool '{tool_name}' not found. Available tools are: {', '.join(self.tools.keys())}"
                    print(observation)
                else:
                    selected_tool = self.tools[tool_name]
                    try:
                        # Execute the selected tool's run method
                        print(f"Executing tool: {tool_name} with argument (first 100 chars): {argument[:100]}...")
                        observation = selected_tool.run(argument)
                        print(f"Tool {tool_name} finished execution.")
                            
                    except Exception as e:
                        observation = f"Error executing tool {tool_name}: {e}"
                        print(observation)

                # --- Observation Step ---                
                messages.append({"role": "user", "content": f"Observation: {observation}"}) # Append result as user message for next LLM cycle

            except Exception as e:
                print(f"Error during ReAct iteration: {e}")
                # Add observation about the error
                messages.append({"role": "user", "content": f"Observation: An error occurred in the previous step: {e}. Please assess the situation and proceed."})                
                continue # Try to recover in the next iteration

        print("--- ReAct Loop Finished: Max Iterations Reached --- ")
        return "Error: Agent reached maximum iterations without providing a final answer."
