# src/tools/base_tool.py

"""Defines the base classes for all tools used by the agent."""

import os
from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field
from openai import OpenAI

# --- Configuration Handling (Simplified) ---
# In a real app, use a more robust method like python-dotenv or config files
# For this example, we assume the API key is set as an environment variable
# We will add a placeholder in config.py later to remind the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY environment variable not set. LLM tools will not function.")
    # You might want to raise an error or handle this more gracefully

# --- Base Tool Class ---

class Tool(ABC, BaseModel):
    """Abstract Base Class for all tools.

    Ensures that every tool has a name, description, argument description,
    and a run method.
    Uses Pydantic for basic validation and structure.
    """
    name: str = Field(..., description="The name of the tool. Should be descriptive and unique.")
    description: str = Field(..., description="A detailed description of what the tool does.")
    arg_description: str = Field(..., description="Description of the expected input argument for the tool's run method.")

    class Config:
        # Allows arbitrary types, useful for things like API clients if needed later
        arbitrary_types_allowed = True

    def model_post_init(self, __context: Any) -> None:
        """Pydantic hook called after model initialization.

        Converts the tool name to a snake_case format suitable for use
        as an identifier by the agent's LLM.
        """
        # Ensure name is lowercase and uses underscores (snake_case)
        self.name = self.name.lower().replace(' ', '_').replace('-', '_')
        # Keep descriptions lowercase for consistency when feeding to LLM
        self.description = self.description.lower()
        self.arg_description = self.arg_description.lower()

    @abstractmethod
    def run(self, argument: str) -> str:
        """The main execution method for the tool.

        This method must be implemented by all subclasses.
        It takes a single string argument and returns a string result.

        Args:
            argument: The input string needed for the tool to perform its task.

        Returns:
            A string containing the result of the tool's execution.
        """
        pass

    def get_tool_description_for_llm(self) -> str:
        """Formats the tool's description for the agent's LLM.

        Provides the LLM with the necessary context to understand
        what the tool does and how to use it (what argument to provide).

        Returns:
            A formatted string describing the tool.
        """
        return f"Tool Name: {self.name}\nDescription: {self.description}\nArgument: {self.arg_description}"

# --- Base LLM Tool Class ---

class LLMTool(Tool):
    """Base class for tools that require an LLM (like OpenAI's GPT models).

    Inherits from Tool and adds an OpenAI client instance.
    """
    client: OpenAI = Field(default_factory=lambda: OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None)

    # Note: The run method is still abstract here.
    # Subclasses like the ReportWritingTool will implement it using the self.client.

    def model_post_init(self, __context: Any) -> None:
        """Ensure the client is initialized if the key exists."""
        super().model_post_init(__context)
        if not self.client and OPENAI_API_KEY:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        elif not OPENAI_API_KEY:
            print(f"Warning: LLMTool '{self.name}' initialized without an OpenAI API key. It may not function.")

# Example of how a concrete tool would inherit (we will build these next):
# class MySearchTool(Tool):
#     name: str = "My Search Tool"
#     description: str = "Searches the web for information."
#     arg_description: str = "The search query."
#
#     def run(self, argument: str) -> str:
#         # Implementation using a search API or library
#         return f"Search results for: {argument}"
#
# class MySummarizerTool(LLMTool):
#     name: str = "My Summarizer Tool"
#     description: str = "Summarizes long text."
#     arg_description: str = "The text to summarize."
#
#     def run(self, argument: str) -> str:
#         if not self.client:
#             return "Error: OpenAI client not available."
#         # Implementation using self.client.chat.completions.create(...)
#         return f"Summary of: {argument[:50]}..."

