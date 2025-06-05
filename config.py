
"""Handles configuration, primarily API keys."""

import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_openai_api_key() -> str | None:
    """Retrieves the OpenAI API key from environment variables."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set the environment variable before running the agent.")
        print("See instructions in src/utils/config.py")
    return key

