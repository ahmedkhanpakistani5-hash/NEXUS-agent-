# NEXUS — Autonomous AI Productivity Agent

## Hackathon
PakAngel Generative AI Hackathon

## Theme
Build Intelligent Agents to Reshape the Future, Unlock Potential & Drive Innovation

## Problem
A normal chatbot is useful for answering a single question, but many real productivity tasks require planning, tool selection, execution, and synthesis. Students, professionals, and teams often need more than a conversational assistant: they need an agent that can read a document, choose relevant tools, perform multi-step work, and produce a final structured result.

## Solution
NEXUS acts like an autonomous AI productivity agent. Instead of simply replying to a prompt, it:

- understands the user's goal,
- creates a structured execution plan,
- chooses the right tools,
- executes those tools,
- combines the outputs,
- and delivers a polished final result.

This demonstrates the difference between a chatbot and an actual AI agent.

## Features
- autonomous planning
- tool selection
- document analysis
- study planning
- quiz generation
- report generation
- execution tracking
- downloadable results

## Architecture

User
↓
NEXUS Agent
↓
Planner
↓
Tool Selection
↓
Tools
↓
Result Synthesis
↓
Final Result

## Tech Stack
- Python
- Streamlit
- Groq
- LLM
- PyPDF
- python-docx

## Project Structure

```text
nexus-ai-agent/
├── app.py
├── agent.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── .streamlit/
│   └── config.toml
│
├── tools/
│   ├── __init__.py
│   ├── document_tool.py
│   ├── study_tool.py
│   ├── quiz_tool.py
│   └── report_tool.py
│
└── utils/
    ├── __init__.py
    └── helpers.py
```

## Installation

1. Open a terminal in the project folder.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run app.py
```

## Streamlit Deployment
To deploy this app on Streamlit Cloud:

1. Push this project to GitHub.
2. Create a new app in Streamlit Cloud.
3. Connect the repository.
4. Set the app file to `app.py`.
5. Add the following secrets in Streamlit Cloud under Secrets:

```toml
GROQ_API_KEY = "your_key_here"
GROQ_MODEL = "openai/gpt-oss-20b"
```

Do not add an actual API key to the repository. The app reads the key from Streamlit Secrets using `st.secrets["GROQ_API_KEY"]` and the model from `st.secrets.get("GROQ_MODEL", "openai/gpt-oss-20b")`.

## Demo
Example prompts:

- Analyze this document, identify the most important topics, create a 7-day study plan and generate practice questions.
- Read this document and create 10 MCQs with answers.
- Analyze this material and create a structured report.
- Summarize this material and create an actionable plan.

## Future Improvements
Possible future enhancements include:

- more tools
- web search
- calendar integration
- email integration
- persistent memory
- multi-agent collaboration

These are future ideas and are not part of the current project.

## License
This project is created for the PakAngel Generative AI Hackathon and is intended for demo and educational use.
