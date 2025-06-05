# AgentPro Research Assistant

This project implements a simple multi-agent AI system based on the ReAct (Reasoning and Acting) framework, inspired by the concepts in the "Build Your Agents from Scratch" Medium articles (Part A & B). It aims to solve the task of researching a topic online and generating a summary report.

This version includes both a command-line interface (CLI) and a graphical user interface (GUI) using Tkinter.

## Project Structure

```
agentpro_research_assistant/
├── main.py                 # Main script to run the agent (CLI version)
├── gui.py                  # Script to run the agent with a Tkinter GUI
├── requirements.txt        # Python dependencies
├── todo.md                 # Development checklist (for reference)
├── README.md               # This file
├── .gitignore              # Files to ignore for Git
└── src/
    ├── __init__.py
    ├── agent.py            # Contains the ReActAgent class
    ├── utils/
    │   ├── __init__.py
    │   └── config.py       # Handles API key configuration
    └── tools/
        ├── __init__.py
        ├── base_tool.py    # Defines base Tool and LLMTool classes
        ├── search_tool.py  # Implements the InternetSearchTool
        └── report_tool.py  # Implements the ReportWritingTool
```

## Features

*   **ReAct Framework:** Uses an LLM (GPT-4o) to reason, select tools, and act in a loop.
*   **Multi-Tool Architecture:** Includes specialized tools for internet search and report writing.
*   **Tkinter GUI:** Provides a simple graphical interface for entering prompts and viewing results.
*   **Extensible:** Designed with base classes (`Tool`, `LLMTool`) to easily add more tools.
*   **Beginner-Friendly:** Code includes comments and explanations suitable for those new to agent development.

## Setup

1.  **Clone the Repository (or Unzip the Archive):** Get the project code onto your local machine.
2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set OpenAI API Key:** This is crucial for the agent to function (both CLI and GUI).
    *   **Method 1: Environment Variable (Recommended):** Set the `OPENAI_API_KEY` environment variable before running the script.
        ```bash
        export OPENAI_API_KEY=\'YOUR_API_KEY_HERE\'
        ```
        (Replace `export` with `set` on Windows Command Prompt, or `$env:OPENAI_API_KEY=\'YOUR_API_KEY_HERE\'` in PowerShell).
    *   **Method 2: `.env` File:**
        1.  Install `python-dotenv`: `pip install python-dotenv`
        2.  Create a file named `.env` in the `agentpro_research_assistant` root directory.
        3.  Add the line: `OPENAI_API_KEY=\'YOUR_API_KEY_HERE\'`
        4.  You would need to modify `gui.py` and `main.py` to load the `.env` file using `from dotenv import load_dotenv; load_dotenv()` at the beginning.

## Usage

Ensure your API key is set correctly (see Setup step 4) and you are in the project root directory (`agentpro_research_assistant/`) in your terminal.

**Option 1: Run with Graphical User Interface (GUI)**

*   This requires a desktop environment (it won't work on headless servers).
*   Run the command:
    ```bash
    python gui.py
    ```
*   A window will appear. Enter your research topic in the input box and click "Start Research".
*   The final report will appear in the text area below.

**Option 2: Run via Command Line (CLI)**

*   Run the command:
    ```bash
    python main.py
    ```
*   The agent will start the ReAct loop for the predefined task in `main.py` ("Research the current state of quantum computing...").
*   Observe the agent's reasoning and action steps printed in the terminal.
*   The final report will be printed at the end.

## Deliverables for Submission

1.  **GitHub Repository:**
    *   Create a new repository on GitHub.
    *   Initialize Git in your local project folder (`git init`).
    *   Add the files (`git add .`).
    *   Commit the files (`git commit -m "Initial commit of AgentPro Research Assistant with GUI"`).
    *   Add the GitHub repository as a remote (`git remote add origin YOUR_REPO_URL`).
    *   Push the code (`git push -u origin main` or `master`).
    *   Share the URL of your GitHub repository.
2.  **Demo Video Recording:**
    *   Record a short video demonstrating the agent running **using the GUI (`python gui.py`)**.
    *   Show the setup (installing requirements, setting API key - **be careful not to expose your key in the video!** You can show setting it as an environment variable without showing the actual key).
    *   Launch the GUI, enter a research topic, and click the button.
    *   Show the final report displayed in the GUI's text area.
    *   Upload the video (e.g., to YouTube, Google Drive, Loom) and share the link.

## Notes

*   **API Key Security:** Never commit your API key directly into the code or share it publicly.
*   **Search Tool Simulation:** The `InternetSearchTool` currently uses a *simulated* search result. In a real-world agent running in an environment like Manus, it would call the actual `info_search_web` tool.
*   **Error Handling:** Basic error handling is included, but a production system would require more robust error management.
*   **Testing:** The agent's performance heavily depends on the LLM and the quality of prompts. Further testing and refinement with a valid API key are recommended.

