# Financial Document Analyzer

A comprehensive financial document analysis system that processes corporate reports, financial statements, and investment documents using AI-powered CrewAI agents.

---

## Project Overview

This system accepts a financial PDF (e.g. Tesla Q2 2025 report), extracts its text, and passes it through a pipeline of 4 specialized AI agents built with CrewAI. Each agent performs a specific role — verification, financial analysis, investment advice, and risk assessment — and returns a comprehensive structured report.

---

## Bugs Found and Fixed

### `requirements.txt`
| # | Bug | Fix |
|---|-----|-----|
| 1 | `pydantic==1.10.13` — CrewAI 0.130.0 requires Pydantic v2 | Changed to `pydantic==2.7.1` |
| 2 | Missing `uvicorn` — needed to run the FastAPI server | Added `uvicorn==0.30.1` |
| 3 | Missing `python-multipart` — required for FastAPI file uploads | Added `python-multipart==0.0.9` |
| 4 | Missing `python-dotenv` — used in code but not listed | Added `python-dotenv==1.0.1` |
| 5 | Missing `pypdf` — needed for PDF reading | Added `pypdf==5.1.0` |
| 6 | Missing `langchain-community` — needed for `PyPDFLoader` | Added `langchain-community==0.3.14` |
| 7 | Missing `duckduckgo-search` — required for web search tool | Added `duckduckgo-search==6.2.1` (tool exists but is currently unused) |
| 8 | Missing `groq` — needed for Groq LLM | Added `groq==0.11.0` |

---

### `tools.py`
| # | Bug | Fix |
|---|-----|-----|
| 1 | `from crewai_tools import tools` — incorrect, nonexistent import | Removed entirely |
| 2 | `Pdf(file_path=path).load()` — `Pdf` is undefined | Replaced with `PyPDFLoader(file_path=path).load()` from `langchain_community` |
| 3 | `FinancialDocumentTool`, `InvestmentTool`, `RiskTool` are plain classes — not valid CrewAI tools | Converted all three to proper `BaseTool` subclasses with `name`, `description`, and `_run()` method |
| 4 | All method definitions missing `self` parameter | Added `self` to all `_run()` methods |
| 5 | Methods defined as `async def` — `BaseTool._run()` must be sync | Changed to regular `def` |

**Note on SerperDevTool:** The original `SerperDevTool` was replaced with a DuckDuckGo-based search tool to avoid paid API dependency. Later, web search was removed from agents entirely because document text is now injected directly into task descriptions — making tool calls unnecessary and avoiding DuckDuckGo rate limits. Future improvement: re-enable web search with proper rate limiting for richer real-time market context.

**Why web search is disabled by default:** To prevent rate-limit errors and keep prompt sizes small, the app relies on the PDF text instead of live web search. You can re-enable it by wiring `search_tool` back into agents and tasks.

---

### `agents.py`
| # | Bug | Fix |
|---|-----|-----|
| 1 | `from crewai.agents import Agent` — wrong import path | Changed to `from crewai import Agent` |
| 2 | `llm = llm` — undefined variable, crashes immediately | Replaced with proper Groq LLM initialization using `GROQ_API_KEY` from environment |
| 3 | `tool=[...]` parameter — wrong parameter name | Changed to `tools=[...]` |
| 4 | `max_iter=1` on all agents — prevents proper reasoning | Changed to `max_iter=5` |
| 5 | `max_rpm=1` on all agents — extreme throttling | Changed to `max_rpm=5` |
| 6 | All agent goals and backstories were deliberately bad prompts — agents told to make up data, ignore documents, fake compliance, recommend sketchy investments | Rewrote all goals and backstories to be professional, accurate, and evidence-based |

---

### `task.py`
| # | Bug | Fix |
|---|-----|-----|
| 1 | Missing imports for `investment_advisor` and `risk_assessor` | Added to import statement |
| 2 | All tasks assigned `agent=financial_analyst` — wrong agents | `investment_analysis` → `investment_advisor`, `risk_assessment` → `risk_assessor`, `verification` → `verifier` |
| 3 | No `context=[]` chaining between tasks — tasks couldn't use prior results | Added `context=[...]` to `analyze_financial_document`, `investment_analysis`, and `risk_assessment` |
| 4 | All task descriptions and `expected_output` were bad prompts — told agents to hallucinate, make up URLs, contradict themselves | Rewrote all descriptions and expected outputs to be clear, structured, and professional |
| 5 | `{file_path}` and `{document_text}` not passed to task descriptions — agents had no access to actual PDF content | Added `{file_path}` and `{document_text}` to all 4 task descriptions |

---

### `main.py`
| # | Bug | Fix |
|---|-----|-----|
| 1 | Endpoint function `async def analyze_financial_document` shadows the imported task of the same name | Renamed endpoint function to `async def analyze_document` |
| 2 | `run_crew` only included 1 agent and 1 task | Added all 4 agents and all 4 tasks |
| 3 | `file_path` passed to `run_crew` but never forwarded to crew's kickoff inputs | Added `file_path` and `document_text` to `financial_crew.kickoff(...)` |
| 4 | `run_crew` (sync/blocking) called directly in async endpoint — blocks the event loop | Wrapped with `loop.run_in_executor(executor, ...)` |
| 5 | No file type validation — any file could be uploaded | Added content type check: only `application/pdf` accepted |
| 6 | `uvicorn.run(..., reload=True)` — `reload=True` doesn't work programmatically | Removed `reload=True` |
| 7 | Missing imports for all agents and tasks | Added all imports |
| 8 | PDF text never extracted or passed to agents — agents had no document content | Added `extract_document_text()` — reads first 5 pages (max 20,000 chars) and passes as `document_text` |

---

## How It Works

```
You upload a PDF + ask a question
        ↓
FastAPI server receives the file
        ↓
PDF text extracted (first 5 pages, max 20,000 chars)
        ↓
4 AI agents run sequentially via CrewAI:

  Agent 1 — Document Verifier
  "Is this actually a financial document?"

  Agent 2 — Financial Analyst
  "What do the numbers say? Answer the user's query."

  Agent 3 — Investment Advisor
  "Should someone invest based on this data?"

  Agent 4 — Risk Assessor
  "What are the real risks in this document?"
        ↓
Combined analysis returned as JSON response
```

---

## Setup Instructions

### Prerequisites
- Python 3.11 (recommended — avoids wheel compilation issues on Windows)
- pip

### API Keys Required
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key at: **https://console.groq.com/keys**

**Note:** OpenAI key is NOT required — this project uses Groq (free tier).

### Install Dependencies

```bash
# Step 1 — Create virtual environment with Python 3.11
py -3.11 -m venv venv

# Step 2 — Activate (Windows)
venv\Scripts\activate

# Step 3 — Upgrade pip
python -m pip install --upgrade pip

# Step 4 — Install dependencies
pip install --no-cache-dir -r requirements.txt
```

### Add Sample Document
Download Tesla Q2 2025 financial update:
```
https://www.tesla.com/sites/default/files/downloads/TSLA-Q2-2025-Update.pdf
```
Save it in the `data/` folder as `TSLA-Q2-2025-Update.pdf`.

---

## Running the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

---

## Testing the API

### Option 1 — Swagger UI (Recommended)
Open in browser:
```
http://localhost:8000/docs
```
- Click `POST /analyze`
- Click **Try it out**
- Upload your PDF
- Enter a query
- Click **Execute**

### Option 2 — curl
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@data/TSLA-Q2-2025-Update.pdf" \
  -F "query=What are the key investment risks in this report?"
```

### Sample Queries
```
What is Tesla's total revenue in Q2 2025?
What are the key financial highlights of this report?
Should I invest in Tesla based on this report?
What are the main financial risks mentioned?
Give me a complete financial analysis including revenue and profit margins.
```

---

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### `GET /`
Health check.

**Response:**
```json
{"message": "Financial Document Analyzer API is running"}
```

#### `POST /analyze`
Upload a financial PDF and receive AI-powered analysis.

**Request (multipart/form-data):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | PDF file | Yes | Financial document to analyze (PDF only) |
| `query` | string | No | Your question (default: general analysis) |

**Response:**
```json
{
  "status": "success",
  "query": "What are the key investment risks?",
  "analysis": "## Risk Assessment Report...",
  "file_processed": "TSLA-Q2-2025-Update.pdf"
}
```

**Error Responses:**
| Code | Meaning |
|------|---------|
| `400` | File is not a PDF |
| `500` | Internal processing error |

---

## Project Structure
```
financial-document-analyzer/
├── agents.py         # 4 CrewAI agent definitions
├── main.py           # FastAPI server, PDF extraction, crew runner
├── README.md         # This file
├── requirements.txt  # Python dependencies
├── task.py           # 4 CrewAI task definitions
├── tools.py          # PDF reader and search tools
├── .env              # API keys (never commit this to git)
├── data/
│   └── TSLA-Q2-2025-Update.pdf
└── outputs/          # Analysis outputs
```

---

## Known Limitations & Future Improvements
- PDF text is truncated to first 5 pages / 20,000 chars to stay within Groq free tier token limits
- Web search is currently disabled to avoid rate limits — future improvement: re-enable with proper throttling for real-time market context
- Groq free tier has token-per-minute limits — wait 60 seconds between requests if you hit rate limits
