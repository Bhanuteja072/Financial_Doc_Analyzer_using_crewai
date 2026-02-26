## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

# FIX: Replaced SerperDevTool with DuckDuckGo — no API key needed, no embedchain dependency
from duckduckgo_search import DDGS
from crewai.tools import BaseTool, tool
from langchain_community.document_loaders import PyPDFLoader
from typing import Optional

## Creating search tool using DuckDuckGo (no API key required)
@tool("Web Search Tool")
def search_tool(query: str) -> str:
    """Search the web for financial information using DuckDuckGo."""
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=5)
        return "\n".join([f"{r['title']}: {r['body']}" for r in results])

## Creating custom pdf reader tool
class FinancialDocumentTool(BaseTool):
    name: str = "Financial Document Reader"
    description: str = "Reads and extracts text content from a PDF financial document. Input should be the file path to the PDF."

    def _run(self, path: str = 'data/sample.pdf') -> str:
        """Tool to read data from a pdf file from a path

        Args:
            path (str, optional): Path of the pdf file. Defaults to 'data/sample.pdf'.

        Returns:
            str: Full Financial Document file
        """
        docs = PyPDFLoader(file_path=path).load()

        full_report = ""
        for data in docs:
            content = data.page_content

            while "\n\n" in content:
                content = content.replace("\n\n", "\n")

            full_report += content + "\n"

        return full_report


## Creating Investment Analysis Tool
class InvestmentTool(BaseTool):
    name: str = "Investment Analysis Tool"
    description: str = "Analyzes financial document data and returns structured investment insights."

    def _run(self, financial_document_data: str) -> str:
        processed_data = financial_document_data

        i = 0
        while i < len(processed_data):
            if processed_data[i:i+2] == "  ":
                processed_data = processed_data[:i] + processed_data[i+1:]
            else:
                i += 1

        return processed_data


## Creating Risk Assessment Tool
class RiskTool(BaseTool):
    name: str = "Risk Assessment Tool"
    description: str = "Performs risk assessment on financial document data and returns a structured risk report."

    def _run(self, financial_document_data: str) -> str:
        return financial_document_data
