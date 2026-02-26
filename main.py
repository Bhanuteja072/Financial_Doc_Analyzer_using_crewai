from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

from langchain_community.document_loaders import PyPDFLoader

from crewai import Crew, Process
# FIX: Added all agents and all tasks to imports
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import analyze_financial_document, investment_analysis, risk_assessment, verification

app = FastAPI(title="Financial Document Analyzer")

# Thread pool for running sync crew in async context
executor = ThreadPoolExecutor()

MAX_PDF_PAGES = 5
MAX_PDF_CHARS = 20000


def extract_document_text(file_path: str, max_pages: int = MAX_PDF_PAGES, max_chars: int = MAX_PDF_CHARS) -> str:
    """Extract a truncated text preview to keep LLM usage under rate limits."""
    docs = PyPDFLoader(file_path=file_path).load()

    parts = []
    for index, doc in enumerate(docs):
        if index >= max_pages:
            break

        content = doc.page_content
        while "\n\n" in content:
            content = content.replace("\n\n", "\n")

        parts.append(content)

    text = "\n".join(parts)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n[Truncated]"

    return text


def run_crew(query: str, file_path: str = "data/sample.pdf", document_text: str = ""):
    """To run the whole crew"""
    # FIX: Added all agents and all tasks — original only had one agent and one task
    financial_crew = Crew(
        agents=[verifier, financial_analyst, investment_advisor, risk_assessor],
        tasks=[verification, analyze_financial_document, investment_analysis, risk_assessment],
        process=Process.sequential,
    )

    # FIX: Added file_path to kickoff inputs so tasks can use it
    result = financial_crew.kickoff({
        'query': query,
        'file_path': file_path,
        'document_text': document_text
    })
    return result


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}


# FIX: Renamed function from analyze_financial_document to analyze_document
# to avoid shadowing the imported task with the same name
@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Analyze financial document and provide comprehensive investment recommendations"""

    # FIX: Added file type validation — only accept PDF files
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Validate query
        if not query or query.strip() == "":
            query = "Analyze this financial document for investment insights"

        # FIX: run_crew is a sync/blocking function — run it in executor to avoid blocking the event loop
        document_text = extract_document_text(file_path)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            executor,
            run_crew,
            query.strip(),
            file_path,
            document_text
        )

        return {
            "status": "success",
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")

    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass  # Ignore cleanup errors


if __name__ == "__main__":
    import uvicorn
    # FIX: Removed reload=True — it doesn't work when running programmatically via __main__
    uvicorn.run(app, host="0.0.0.0", port=8000)
