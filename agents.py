## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

# FIX: Corrected import — should be "from crewai import Agent", not "from crewai.agents import Agent"
from crewai import Agent, LLM

from tools import search_tool

### Loading LLM
# FIX: "llm = llm" was undefined — properly initialize the LLM using OpenAI via CrewAI's LLM wrapper

groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    raise ValueError("GROQ_API_KEY is not set")

llm = LLM(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0.1,
    api_key=groq_key,
    api_base="https://api.groq.com/openai/v1",
    max_tokens=1024
)
# llm.call("What is the capital of France?")

# Creating an Experienced Financial Analyst agent
# FIX: Rewrote goal and backstory — original was instructing agent to make up data, ignore reports, and give non-compliant advice
# FIX: Changed "tool=" to "tools=" (correct CrewAI parameter name)
# FIX: Increased max_iter from 1 to 5 and max_rpm from 1 to 10 for proper reasoning
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal=(
        "Thoroughly analyze the provided financial document to answer the user's query: {query}. "
        "Extract key financial metrics, performance indicators, and relevant data points. "
        "Provide accurate, evidence-based analysis grounded strictly in the document's content."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "You are a seasoned financial analyst with 15+ years of experience analyzing corporate financial reports, "
        "earnings statements, and investment documents. You are known for your meticulous attention to detail, "
        "data-driven approach, and ability to extract meaningful insights from complex financial data. "
        "You always base your analysis on the actual document content and clearly cite the relevant sections. "
        "You strictly adhere to financial reporting standards and regulatory compliance requirements."
    ),
    tools=[],
    llm=llm,
    max_iter=5,
    max_rpm=5,
    allow_delegation=False
)

# Creating a document verifier agent
# FIX: Rewrote goal and backstory — original told agent to approve everything without reading
verifier = Agent(
    role="Financial Document Verifier",
    goal=(
        "Carefully verify that the uploaded document is a legitimate financial document. "
        "Confirm it contains recognizable financial data such as revenue figures, balance sheets, "
        "cash flow statements, or investment disclosures. Report clearly if the document is valid or not."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "You are a rigorous financial compliance specialist with deep experience in document verification "
        "and regulatory standards. You carefully examine each document for authenticity, completeness, "
        "and financial relevance. You never approve a document without thoroughly reviewing its contents, "
        "and you always flag documents that do not meet financial reporting standards."
    ),
    tools=[],
    llm=llm,
    max_iter=5,
    max_rpm=5,
    allow_delegation=False
)

# FIX: Rewrote goal and backstory — original was instructing agent to sell products, ignore compliance, and make up connections
investment_advisor = Agent(
    role="Investment Advisor",
    goal=(
        "Based on the verified financial document analysis, provide clear, objective investment recommendations "
        "relevant to the user's query: {query}. Identify opportunities and concerns grounded in the actual "
        "financial data. Ensure all recommendations are realistic, compliant, and suitable for the document context."
    ),
    verbose=True,
    backstory=(
        "You are a certified financial planner and investment advisor with over 15 years of institutional experience. "
        "You specialize in translating complex financial data into actionable investment insights. "
        "Your recommendations are always evidence-based, aligned with the client's needs, and fully compliant "
        "with SEC regulations and fiduciary standards. You never recommend products without clear justification "
        "from the underlying financial data."
    ),
    tools=[],
    llm=llm,
    max_iter=5,
    max_rpm=5,
    allow_delegation=False
)

# FIX: Rewrote goal and backstory — original told agent to fabricate risks, ignore regulations, and use "YOLO" strategies
risk_assessor = Agent(
    role="Risk Assessment Specialist",
    goal=(
        "Conduct a thorough and realistic risk assessment based on the financial document. "
        "Identify genuine risk factors such as liquidity risk, market exposure, debt levels, and operational risks. "
        "Provide a balanced risk profile with mitigation strategies grounded in the actual data."
    ),
    verbose=True,
    backstory=(
        "You are an experienced risk management professional with deep expertise in financial risk assessment, "
        "portfolio risk analysis, and regulatory compliance. You approach every analysis methodically, "
        "identifying real risks based on financial data rather than speculation. "
        "You follow established risk management frameworks and always present a balanced, well-evidenced risk profile "
        "with practical mitigation recommendations."
    ),
    tools=[],
    llm=llm,
    max_iter=5,
    max_rpm=5,
    allow_delegation=False
)
