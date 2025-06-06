"""
RCA Agent using BeeAI with IBM Granite via Ollama.

This script analyzes an error message and associated log file to determine
the root cause, provide a summary, and suggest a fix.

Original Author: Kenneth (Alex) Jenkins - https://alexj.io
"""

import argparse
import asyncio
import os
import re
from beeai_framework.backend.chat import ChatModel
from beeai_framework.backend.message import UserMessage, AssistantMessage

def build_prompt(error_desc, log_lines):
    """
    Constructs a prompt for the LLM to perform Root Cause Analysis (RCA).
    
    The prompt includes:
    - A description of the error reported by the user.
    - An excerpt from the service log to provide context.
    
    This function is part of the agent's information sourcing mechanism, where basic context is provided to the LLM.
    """
    return f"""You are an expert in debugging distributed web systems.

The user is reporting the following error:
"{error_desc}"

Here is an excerpt from the service log:

{log_lines}

Please identify the likely root cause and suggest a debugging strategy. Structure your response with clear sections:
- Root Cause
- Evidence
- Suggested Fix
- Further Questions
"""

async def perform_rca(error_desc, logfile_path):
    """
    Performs Root Cause Analysis (RCA) based on the provided error description and log file.
    
    This function is responsible for:
    - Reading the log file to gather context.
    - Constructing a prompt for the LLM.
    - Sending the prompt to the LLM and extracting the response.
    
    The agent sources information by reading a static log file, which is a basic approach to information gathering.
    """
    # Read and preprocess logs
    if not os.path.exists(logfile_path):
        raise FileNotFoundError(f"Log file not found: {logfile_path}")

    with open(logfile_path, 'r') as f:
        log_lines = f.read()

    # Build the prompt for the model
    prompt = build_prompt(error_desc, log_lines)

    # Initialize the Granite model via BeeAI
    model = ChatModel.from_name("ollama:granite3.3:8b-beeai")

    # Construct UserMessage properly
    user_msg = UserMessage(prompt)

    try:
        response = await model.create(messages=[user_msg])
        # Extract only the text content from the response
        if isinstance(response, list) and len(response) > 0:
            if hasattr(response[0], "text"):
                return response[0].text
            return str(response[0])
        elif hasattr(response, "messages"):
            messages = response.messages
            if isinstance(messages, list) and len(messages) > 0 and hasattr(messages[0], "text"):
                return messages[0].text
            return str(messages)
        elif hasattr(response, "text"):
            return response.text
        else:
            return str(response)
    except Exception as e:
        raise Exception(f"Failed to get response from model: {e}")

def parse_args():
    """
    Parses command-line arguments for the RCA agent.
    
    This function is part of the agent's mechanism to engage with the user through a command-line interface,
    allowing the user to report a problem and specify the log file for analysis.
    """
    parser = argparse.ArgumentParser(description="Root Cause Analysis using Granite via BeeAI")
    parser.add_argument('--error', type=str, required=True, help='The user-facing error message')
    parser.add_argument('--logfile', type=str, required=True, help='Path to the service log file')
    return parser.parse_args()

def main():
    """
    Main function to run the RCA agent.
    
    This function:
    - Parses command-line arguments.
    - Calls the perform_rca function to conduct the analysis.
    - Prints the analysis report with proper formatting, supporting markdown text formatting for TUI output.
    
    The agent's action when a problem is identified is to inform the user and suggest a fix, as part of the RCA process.
    """
    args = parse_args()
    try:
        analysis = asyncio.run(perform_rca(args.error, args.logfile))
        print("=== IBM Granite Root Cause Analysis Report ===")
        if isinstance(analysis, str):
            # Bold any text enclosed in double asterisks
            bolded = re.sub(r'\*\*(.*?)\*\*', r'\033[1m\1\033[0m', analysis)
            # Underline and bold any line that starts with '##'
            underlined = re.sub(r'^##\s*(.*?)$', r'\033[1;4m\1\033[0m', bolded, flags=re.MULTILINE)
            # Split on '\n' and print each line for correct newlines
            for line in underlined.split('\\n'):
                print(line)
        else:
            print(analysis)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()