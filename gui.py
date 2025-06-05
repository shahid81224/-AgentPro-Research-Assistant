"""Tkinter GUI for the ReAct Research Agent - Enhanced Look & Markdown Rendering"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, font as tkFont
import threading
import queue
import sys
import os
import re # Import regex for parsing

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import get_openai_api_key
from src.tools.search_tool import InternetSearchTool
from src.tools.report_tool import ReportWritingTool
from src.agent import ReActAgent

class AgentGUI:
    def __init__(self, master):
        self.master = master
        master.title("AgentPro Research Assistant")
        master.geometry("750x550")
        master.configure(bg='#f0f0f0')

        # --- Configuration & Styling ---
        self.api_key = get_openai_api_key()
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=5)
        style.configure('TEntry', font=('Segoe UI', 10), padding=5)
        style.configure('Status.TLabel', font=('Segoe UI', 9), padding=5)

        # --- Main Frame ---
        main_frame = ttk.Frame(master, padding="10 10 10 10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- Input Frame ---
        input_frame = ttk.Frame(main_frame, padding="5 5 5 5")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="Enter Research Topic:").pack(side=tk.LEFT, padx=(0, 5))
        self.prompt_entry = ttk.Entry(input_frame)
        self.prompt_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        self.prompt_entry.focus_set()

        self.start_button = ttk.Button(input_frame, text="Start Research", command=self.start_agent_thread)
        self.start_button.pack(side=tk.LEFT)

        # --- Output Frame ---
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(output_frame, text="Agent Output:").pack(anchor=tk.W, pady=(0, 5))
        
        # Define fonts
        self.default_font = tkFont.Font(family="Segoe UI", size=10)
        self.bold_font = tkFont.Font(family="Segoe UI", size=10, weight="bold")
        self.heading_font = tkFont.Font(family="Segoe UI", size=12, weight="bold")

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, 
                                                    font=self.default_font, 
                                                    relief=tk.SUNKEN, 
                                                    borderwidth=1,
                                                    padx=5, pady=5)
        self.output_text.pack(expand=True, fill=tk.BOTH)
        
        # Define tags for formatting
        self.output_text.tag_configure("heading", font=self.heading_font, spacing1=5, spacing3=5) # Add spacing around headings
        self.output_text.tag_configure("bold", font=self.bold_font)
        # Add a tag for list items if needed (e.g., for indentation)
        self.output_text.tag_configure("list_item", lmargin1=20, lmargin2=20) 

        self.output_text.configure(state='disabled')

        # --- Status Bar ---
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Enter a topic and click 'Start Research'.")
        status_bar = ttk.Label(master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, style='Status.TLabel')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Agent Setup ---
        self.agent = None
        self.result_queue = queue.Queue()

        if not self.api_key:
            messagebox.showerror("API Key Error", "OPENAI_API_KEY environment variable not set. Agent will not function.")
            self.start_button.configure(state='disabled')
            self.status_var.set("Error: OPENAI_API_KEY not set!")
        else:
            self.initialize_agent()

    def initialize_agent(self):
        if not self.api_key:
            return
        try:
            search_tool = InternetSearchTool()
            report_tool = ReportWritingTool()
            available_tools = [search_tool, report_tool]
            self.agent = ReActAgent(tools=available_tools)
            self.status_var.set("Agent initialized. Ready.")
        except Exception as e:
            messagebox.showerror("Agent Initialization Error", f"Failed to initialize agent: {e}")
            self.start_button.configure(state='disabled')
            self.status_var.set("Error: Agent initialization failed.")

    def start_agent_thread(self):
        prompt = self.prompt_entry.get().strip()
        if not prompt:
            messagebox.showwarning("Input Error", "Please enter a research topic.")
            return
        if not self.agent:
            messagebox.showerror("Error", "Agent is not initialized. Check API key and restart.")
            return

        self.start_button.configure(state='disabled')
        self.output_text.configure(state='normal')
        self.output_text.delete(1.0, tk.END)
        # Insert initial message without tags
        # self.output_text.insert(tk.END, f"Starting research for: {prompt}\n" + "-"*50 + "\n")
        # Insert initial message with bold label
        self.output_text.insert(tk.END, "Starting research for: ", ("bold",))
        self.output_text.insert(tk.END, f"{prompt}\n" + "-"*50 + "\n")
        self.output_text.configure(state='disabled')
        self.status_var.set("Agent running...")

        self.agent_thread = threading.Thread(target=self.run_agent_task, args=(prompt,), daemon=True)
        self.agent_thread.start()
        self.master.after(100, self.check_queue)

    def run_agent_task(self, task):
        try:
            final_result = self.agent.run(task)
            self.result_queue.put(final_result)
        except Exception as e:
            # Put error message in queue to display in GUI
            error_msg = f"Error during agent execution: {e}"
            self.result_queue.put(error_msg)
            # Also print to console for debugging
            print(error_msg, file=sys.stderr)

    def insert_formatted_text(self, text_widget, text):
        """Inserts text into the widget, applying formatting based on simple Markdown."""
        # Basic bold handling: **text**
        # Basic heading handling: ## text
        # Basic list handling: - text or * text
        
        # Split text into lines to process individually
        for line in text.split('\n'):
            stripped_line = line.strip()
            tags_to_apply = []
            text_to_insert = line # Default to the original line

            # Check for headings
            if stripped_line.startswith('## '):
                tags_to_apply.append("heading")
                text_to_insert = stripped_line[3:] # Remove '## '
            elif stripped_line.startswith('# '): # Handle H1 as well
                tags_to_apply.append("heading")
                text_to_insert = stripped_line[2:] # Remove '# '
            
            # Check for list items (simple version)
            if stripped_line.startswith(('-', '*')) and len(stripped_line) > 1 and stripped_line[1] == ' ':
                 tags_to_apply.append("list_item")
                 # Keep the list marker for now, or remove it: text_to_insert = stripped_line[2:]
                 text_to_insert = stripped_line # Keep marker for visual cue

            # Apply tags and insert the line
            # Handle inline bold: find all **text** occurrences
            start_index = text_widget.index(tk.END + "-1c") # Get index before newline
            segments = re.split(r'(\*\*.*?\*\*)', text_to_insert) # Split by bold markers
            
            for segment in segments:
                if segment.startswith('**') and segment.endswith('**') and len(segment) > 4:
                    # Insert bold segment without markers
                    text_widget.insert(tk.END, segment[2:-2], tuple(tags_to_apply + ["bold"]))
                elif segment: # Insert normal segment
                    text_widget.insert(tk.END, segment, tuple(tags_to_apply))
            
            text_widget.insert(tk.END, '\n') # Add newline after processing the line

    def check_queue(self):
        try:
            message = self.result_queue.get_nowait()
            self.output_text.configure(state='normal')
            
            # Insert header without tags
            #self.output_text.insert(tk.END, "\n" + "="*50 + "\nFinal Result:\n" + "="*50 + "\n")
            
            # Insert the formatted message content
            self.insert_formatted_text(self.output_text, message)
            
            self.output_text.configure(state='disabled')
            self.output_text.see(tk.END)
            self.status_var.set("Agent finished.")
            self.start_button.configure(state='normal')

        except queue.Empty:
            if self.agent_thread.is_alive():
                self.master.after(100, self.check_queue)
            else:
                self.status_var.set("Agent finished (unexpectedly?). Ready.")
                self.start_button.configure(state='normal')
        except Exception as e:
             # Catch errors during GUI update
             print(f"Error updating GUI: {e}", file=sys.stderr)
             self.status_var.set(f"GUI Update Error: {e}")
             self.start_button.configure(state='normal') # Re-enable button on error

if __name__ == "__main__":
    root = tk.Tk()
    # Set a default font - applied via styles and tag configs now
    # default_font = tkFont.nametofont("TkDefaultFont")
    # default_font.configure(family="Segoe UI", size=10)
    # root.option_add("*Font", default_font)
    
    gui = AgentGUI(root)
    root.mainloop()

