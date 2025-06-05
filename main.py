# main.py

"""Main script to run the ReAct Research Agent."""

import sys
import os

# Add the src directory to the Python path
# This allows us to import modules from src like src.agent, src.tools, etc.
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import get_openai_api_key
from src.tools.search_tool import InternetSearchTool
from src.tools.report_tool import ReportWritingTool
from src.agent import ReActAgent

def main():
    """Sets up and runs the ReAct agent for a research task."""
    print("--- Initializing Research Agent --- ")

    # 1. Check for API Key
    # The agent and LLM tools rely on this key.
    api_key = get_openai_api_key()
    if not api_key:
        # Error message is printed within get_openai_api_key()
        return # Exit if key is not found
    print("OpenAI API Key found.")

    # 2. Initialize Tools
    # Create instances of the tools the agent can use.
    print("Initializing tools...")
    try:
        search_tool = InternetSearchTool()
        report_tool = ReportWritingTool()
        available_tools = [search_tool, report_tool]
        print(f"Tools initialized: {[tool.name for tool in available_tools]}")
    except Exception as e:
        print(f"Error initializing tools: {e}")
        return

    # 3. Initialize Agent
    # Pass the available tools to the agent.
    print("Initializing ReAct Agent...")
    try:
        agent = ReActAgent(tools=available_tools)
        print("Agent initialized successfully.")
    except Exception as e:
        print(f"Error initializing agent: {e}")
        return

    # 4. Define the Task
    # Specify the research question or task for the agent.
    # research_task = "What are the main benefits and drawbacks of using Python for web development?"
    research_task = "Research the current state of quantum computing and provide a brief summary report."
    print(f"\n--- Starting Task ---\nTask: {research_task}")
    # 5. Run the Agent
    # Execute the agent's run method with the task.
    # This starts the ReAct loop.
    try:
        final_result = agent.run(research_task)
    except Exception as e:
        print(f"\n--- An error occurred during agent execution: {e} ---")
        final_result = "Agent execution failed due to an error."

    # 6. Print the Final Result
    print("\n--- Task Finished --- ")
    print("\nFinal Result from Agent:")
    print("="*30)
    print(final_result)
    print("="*30)

if __name__ == "__main__":
    main()

