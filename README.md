# Agentic AI Portfolio

A collection of autonomous agents, multi-agent systems (MAS), and standardized tool integrations using the Model Context Protocol (MCP). This repository tracks my progress from single-purpose scripts to complex, reasoning-based AI workflows.

---

## Project Showcase

### MCP and Tool-Calling
* **MCP_Projects:** My core implementation of the Model Context Protocol. It features ReAct (Reason + Act) agents that can browse the local filesystem, read/write files, and fetch web data by connecting to external Node.js and Python servers.
* **BeepBoop:** A testing ground for advanced tool-calling logic. This is where I experiment with how LLMs handle complex function schemas and error recovery.

### Finance and Sales Agents
* **FinanceAgent:** A specialized engine powered by Google Gemini for financial data processing. It uses structured tool calling to analyze market trends and generate reports.
* **Agentic_SDR:** An automated Sales Development Representative. This agent manages lead outreach and sales communication, mimicking a human SDR workflow to handle initial prospect engagement.

### Multi-Agent Orchestration
* **LangGraph_projects:** High-level stateful agents. These projects use LangGraph to create cycles and checkpoints, allowing agents to remember previous steps and self-correct during long-running tasks.
* **crew_projects:** Team-based AI. Using CrewAI, I built collaborative squads (Researchers, Coders, and Managers) that work together to solve engineering and stock-picking problems.
* **claude_code_projects:** Experiments using Anthropic’s Claude Code to automate e-commerce demonstrations and backend integrations.

---

## Technical Architecture

* **Standardized Interfaces:** Using MCP to decouple the LLM from the tools, making my agents provider-agnostic (they can switch between OpenAI, Claude, and Gemini easily).
* **Autonomous Logic:** Implementing the ReAct loop, which allows the AI to decide when it needs to use a tool rather than following a hardcoded path.
* **Secure Sandboxing:** All filesystem agents are restricted to specific workspace directories to ensure safe execution on the host machine.
