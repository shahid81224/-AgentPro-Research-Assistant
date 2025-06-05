# src/tools/report_tool.py

"""Defines the tool for writing reports based on provided information."""

from .base_tool import LLMTool
from pydantic import Field

class ReportWritingTool(LLMTool):
    """A tool that uses an LLM to write a report based on provided text.

    Inherits from LLMTool to get access to the OpenAI client.
    """
    name: str = Field("Report Writing Tool", description="The name of the tool.")
    description: str = Field(
        "Takes input text (e.g., research findings, search results) and writes a concise, well-structured report based on it. "
        "Useful for summarizing information or drafting documents.",
        description="A detailed description of what the tool does."
    )
    arg_description: str = Field(
        "The text content that needs to be summarized and formatted into a report.",
        description="Description of the expected input argument for the tool's run method."
    )

    def run(self, argument: str) -> str:
        """Executes the report writing task using the LLM.

        Args:
            argument: The input text to be turned into a report.

        Returns:
            A string containing the generated report, or an error message.
        """
        print(f"Executing ReportWritingTool with input text (length: {len(argument)})")

        if not self.client:
            return "Error: OpenAI client is not available. Cannot generate report. Please check API key setup."

        if not argument or argument.strip() == "":
            return "Error: Input text for the report is empty."

        system_prompt = (
            "You are a helpful assistant specialized in writing concise and informative reports. "
            "Based on the provided text, generate a well-structured report. "
            "Focus on clarity, key findings, and a professional tone. Use markdown for formatting if appropriate (e.g., headings, bullet points)."
        )
        user_prompt = f"Please generate a report based on the following text:\n\n---\n{argument}\n---"

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o", # Or another suitable model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7, # Adjust for creativity vs. factuality
                max_tokens=1000, # Adjust based on expected report length
            )
            report = response.choices[0].message.content
            print("--- Report Generation Successful ---")
            return report

        except Exception as e:
            error_message = f"Error during report generation: {e}"
            print(f"--- {error_message} ---")
            return error_message

