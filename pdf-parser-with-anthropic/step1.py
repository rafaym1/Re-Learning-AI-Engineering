from httpcore import stream
import pdfplumber
import anthropic
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed
import json
from datetime import datetime

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

print("API Key loaded:", api_key[:12], "...")


COST_LOG = "cost_log.json"
# Assuming the costs here just for the sake of it
INPUT_COST_PER_MTOK = 1.00
OUTPUT_COST_PER_MTOK = 5.00

def log_cost(response, label=""):
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    cost = (input_tokens / 1_000_000 * INPUT_COST_PER_MTOK) + \
           (output_tokens / 1_000_000 * OUTPUT_COST_PER_MTOK)

    entry = {
        "time": datetime.now().isoformat(),
        "label": label,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": round(cost, 6)
    }

    try:
        with open(COST_LOG, "r") as f:
            log = json.load(f)
    except FileNotFoundError:
        log = []

    log.append(entry)
    with open(COST_LOG, "w") as f:
        json.dump(log, f, indent=2)

    return cost

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

#M1
#steaming text here
def parse_invoice_with_claude(invoice_text):
    prompt = f"Extract invoice fields as JSON:\n{invoice_text}"

    full_response = ""
    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text
    print()
    response = stream.get_final_message()
    cost = log_cost(response, label="extract_metadata")
    print(f"Query cost: ${cost:.6f}")
    return full_response



@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def extract_metadata_structured(paper_text):
    schema_tool = [{
        "name": "record_metadata",
        "description": "Record extracted paper metadata",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "authors": {"type": "array", "items": {"type": "string"}},
                "key_claim": {"type": "string"},
                "limitations": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["title", "authors", "key_claim", "limitations"]
        }
    }]

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        tools=schema_tool,
        tool_choice={"type": "tool", "name": "record_metadata"},
        messages=[{"role": "user", "content": f"Extract metadata from this paper:\n{paper_text}"}],
    )
    cost = log_cost(response, label="extract_metadata")
    print(f"Query cost: ${cost:.6f}")

    tool_block = next(b for b in response.content if b.type == "tool_use")
    return tool_block.input  

def print_total_spend():
    with open(COST_LOG, "r") as f:
        log = json.load(f)
    total = sum(e["cost"] for e in log)
    print(f"\nTotal spend this session: ${total:.6f}")

if __name__ == "__main__":
    pdf_path = r"path to your doc which is in the same folder as this code"
    pdf_text = extract_text_from_pdf(pdf_path)

    metadata = extract_metadata_structured(pdf_text)
    print(metadata)
    print_total_spend()