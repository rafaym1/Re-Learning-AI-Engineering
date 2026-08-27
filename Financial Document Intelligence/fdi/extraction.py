import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

from fdi.schema import Document

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-3.6-flash"


class FinancialHighlight(BaseModel):
    metric: str
    value: str
    fiscal_period: str
    source_excerpt: str


def extract_financial_highlights(document: Document) -> list[FinancialHighlight]:
    """Ask Gemini to pull key financial line items out of a filing, each grounded in a verbatim source excerpt."""
    prompt = (
        "Extract the key financial highlights (e.g. revenue, net income, total assets, "
        "total debt) from this financial filing. For each one, give the exact fiscal period "
        "and a short verbatim excerpt from the text that supports the figure.\n\n"
        f"{document.text}"
    )
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[FinancialHighlight],
        ),
    )
    return response.parsed
