## Importing libraries and files
from crewai import Task

# FIX: Added missing imports for investment_advisor and risk_assessor
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import search_tool

## Verification task — runs first to confirm document is valid
# FIX: Changed agent from financial_analyst to verifier (correct responsible agent)
# FIX: Rewrote description and expected_output — original told agent to hallucinate and guess
verification = Task(
    description=(
        "Verify that the uploaded financial document at this file path is a legitimate financial report: {file_path}. "
        "Use this document_text (a truncated excerpt of the PDF) to verify its contents: {document_text} "
        "Check for the presence of financial data such as revenue figures, earnings, balance sheet items, "
        "cash flow statements, or investment disclosures. "
        "Confirm whether this is a valid financial document and summarize what type of report it appears to be."
    ),
    expected_output=(
        "A clear verification report stating:\n"
        "1. Whether the document is a valid financial document (Yes/No)\n"
        "2. The type of financial document (e.g., quarterly earnings report, annual report, etc.)\n"
        "3. Key sections identified in the document\n"
        "4. Any concerns about document completeness or authenticity"
    ),
    agent=verifier,
    async_execution=False
)

## Creating a task to help solve user's query
# FIX: Rewrote description and expected_output — original told agent to make up URLs, contradict itself, and use imagination
analyze_financial_document = Task(
    description=(
        "Using the verified financial document, conduct a comprehensive financial analysis to address "
        "the user's query: {query}. "
        "Use this document_text (a truncated excerpt of the PDF) for analysis: {document_text} "
        "Read the document carefully and extract key financial metrics including revenue, profit margins, "
        "growth rates, debt levels, and any other relevant indicators. "
        "Base all findings strictly on the document content."
    ),
    expected_output=(
        "A structured financial analysis report containing:\n"
        "1. Executive Summary — key findings relevant to the query\n"
        "2. Financial Performance Overview — revenue, profit, growth trends\n"
        "3. Key Financial Metrics — with actual figures from the document\n"
        "4. Market Context — relevant industry or market comparisons\n"
        "5. Notable Observations — any significant items from the document"
    ),
    agent=financial_analyst,
    tools=[],
    # FIX: Added context so this task uses the verification result
    context=[verification],
    async_execution=False,
)

## Creating an investment analysis task
# FIX: Changed agent from financial_analyst to investment_advisor
# FIX: Rewrote description and expected_output — original told agent to make up connections and recommend meme stocks
investment_analysis = Task(
    description=(
        "Based on the financial analysis of the document, provide clear and objective investment recommendations "
        "relevant to the user's query: {query}. "
        "Use this document_text (a truncated excerpt of the PDF) for evidence: {document_text} "
        "Identify investment opportunities or concerns directly supported by the document data. "
        "Consider the company's financial health, growth trajectory, and any stated strategic initiatives. "
        "All recommendations must be grounded in the document's actual figures and findings."
    ),
    expected_output=(
        "A structured investment recommendation report containing:\n"
        "1. Investment Thesis — overall assessment based on the financial data\n"
        "2. Key Opportunities — specific data-backed opportunities identified\n"
        "3. Key Concerns — financial red flags or areas of caution\n"
        "4. Recommendation — Buy / Hold / Sell with clear justification from the document\n"
        "5. Suggested Next Steps — practical actions for an investor"
    ),
    agent=investment_advisor,
    tools=[],
    # FIX: Added context so this task builds on the financial analysis
    context=[verification, analyze_financial_document],
    async_execution=False,
)

## Creating a risk assessment task
# FIX: Changed agent from financial_analyst to risk_assessor
# FIX: Rewrote description and expected_output — original told agent to fabricate risks and ignore real data
risk_assessment = Task(
    description=(
        "Conduct a thorough risk assessment based on the financial document and the user's query: {query}. "
        "Use this document_text (a truncated excerpt of the PDF) for evidence: {document_text} "
        "Identify real risk factors present in the data such as high debt-to-equity ratio, declining revenues, "
        "liquidity concerns, market concentration risks, or regulatory exposure. "
        "Provide a balanced risk profile with realistic mitigation strategies. "
        "Do not fabricate risks — only report what is genuinely evidenced in the document."
    ),
    expected_output=(
        "A structured risk assessment report containing:\n"
        "1. Overall Risk Rating — Low / Medium / High with justification\n"
        "2. Identified Risk Factors — each with supporting evidence from the document\n"
        "3. Risk Severity Matrix — categorized by likelihood and impact\n"
        "4. Mitigation Strategies — practical, evidence-based recommendations\n"
        "5. Risk Summary — concise overview for decision-making"
    ),
    agent=risk_assessor,
    # FIX: Added context so risk assessment builds on previous analysis
    context=[verification, analyze_financial_document],
    async_execution=False,
)
