# AI Agents, Tools & Automation

A beginner-friendly, GitHub-ready AI agent project demonstrating LLM tool calling, task management, SQLite persistence, and conversation memory.

## Learning objectives

- Understand the difference between chatbots and tool-using agents.
- Use function/tool calling to let an LLM select actions.
- Connect an LLM to application tools and a SQLite database.
- Persist tasks and conversation history.
- Apply basic safety controls and evaluate agent behavior.

## Architecture

```text
User
 |
 v
CLI application
 |
 v
OpenAI model ---- decides whether a tool is needed
 |                            |
 |                     Function call
 |                            |
 |                 +----------+----------+
 |                 |          |          |
 |              Calculator  Task DB   List tasks
 |                            |
 +<---------------------------+
 |
 v
Final response
```

## Project structure

```text
AI-Agent-Tools-Automation/
├── agent/
│   ├── __init__.py
│   ├── database.py
│   ├── tools.py
│   └── runner.py
├── .env.example
├── .gitignore
├── requirements.txt
├── main.py
├── linkedin_post.md
└── README.md
```

## 1. Requirements

- Python 3.10+
- An OpenAI API key
- Internet connection for model requests

## 2. Setup

```bash
# Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your own API key:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Never commit `.env` or paste API keys into source code. If a key has been exposed, revoke it and create a new one.

## 3. Run

```bash
python main.py
```

Try these prompts:

- `What is 125 multiplied by 8?`
- `Add a task to study LangGraph tomorrow.`
- `Show my tasks.`
- `Mark task 1 as completed.`
- `What tasks do I still have?`

Type `exit` to stop the application.

## 4. Tools included

| Tool | Purpose |
|---|---|
| `calculate` | Evaluates basic arithmetic expressions safely |
| `add_task` | Saves a task in SQLite |
| `list_tasks` | Retrieves saved tasks |
| `complete_task` | Marks a task as completed |

The model chooses tools through function calling. The Python application validates arguments and executes only the registered functions.

## 5. Agent vs chatbot

A basic chatbot primarily responds with text. This agent can select registered tools, execute actions, inspect results, and then formulate a response. Tool use is not unrestricted: only explicitly implemented functions are available.

## 6. State and memory

- **Persistent application state:** tasks are stored in `agent_memory.db` using SQLite.
- **Conversation context:** recent turns are retained in memory while the CLI process is running.
- **Restart behavior:** tasks persist after restarting; the in-process conversation context resets.

## 7. Safety and limitations

- The agent can execute only the tools defined in `agent/tools.py`.
- Tool inputs are validated; arithmetic is parsed with an AST allowlist rather than Python `eval`.
- The agent does not execute shell commands, arbitrary SQL, or arbitrary URLs.
- Review tool actions and outputs. Do not give an agent unrestricted access to sensitive systems.
- The model may misunderstand a request or produce an incorrect answer. Verify important outputs.
- This demo does not provide authentication, multi-user isolation, or production-grade deployment controls.

## 8. Suggested evaluation

Run each test and record whether the expected tool was selected and whether the result was correct.

| Test | Expected behavior |
|---|---|
| Arithmetic request | Calls calculator and returns correct result |
| Add task | Saves one task and confirms its ID |
| List tasks | Retrieves saved tasks |
| Complete valid task | Updates task status |
| Complete unknown task | Reports that the task was not found |
| General question | Responds without requiring a tool |

Suggested metrics: tool-selection accuracy, tool execution success rate, answer correctness, latency, and unsafe-action rate.

## 9. GitHub delivery

```bash
git init
git add .
git commit -m "Build AI agent with tools and SQLite memory"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/AI-Agent-Tools-Automation.git
git push -u origin main
```

Before pushing, confirm `.env` and `agent_memory.db` are not staged.

## 10. Future improvements

- Add a FastAPI backend and web interface.
- Add a human approval step before sensitive actions.
- Add a vector database for semantic memory.
- Add LangGraph for explicit multi-step state transitions.
- Add unit tests, tracing, and structured evaluation.
- Integrate a trusted external API with scoped credentials.
