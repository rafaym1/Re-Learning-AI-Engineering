import json
import os
import re

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

from fdi.knowledge_base import load_category_facts

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], max_retries=5)
MODEL = "claude-sonnet-5"

TONE_INSTRUCTIONS = (
    "Write in the persuasive, confident, data-driven tone of a sell-side investment bank's "
    "Confidential Information Memorandum. Use concrete numbers to support every claim. "
    "Do not invent facts -- use only the context provided."
)

SECTIONS = [
    ("Executive Summary", "A concise, compelling overview of the investment opportunity: what the company does, its scale, and why it is attractive."),
    ("Company Overview", "The company's history, business model, operating segments, and scale of operations."),
    ("Market Overview and Company Positioning", "The industry the company operates in and how it is positioned relative to competitors."),
    ("Product Overview", "The company's core products/services and what differentiates them."),
    ("Clients, Sales & Marketing Overview", "How the company acquires and retains customers, and its marketing approach."),
    ("Growth Strategy", "The company's strategy and concrete plans for future growth."),
    ("Financial Overview", "A summary of the company's key financial results and trends, citing specific figures."),
]


def generate_section(name: str, instructions: str, context: str) -> str:
    """Draft one memo section in a single Claude call, grounded only in the given context."""
    prompt = (
        f"{TONE_INSTRUCTIONS}\n\n"
        f"Write the '{name}' section of a Confidential Information Memorandum for Planet Fitness, Inc.\n"
        f"Section focus: {instructions}\n\n"
        f"Context:\n{context}"
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return next(block.text for block in response.content if block.type == "text")


class UnverifiedClaim(BaseModel):
    claim: str
    reason: str


class VerificationResult(BaseModel):
    unverified_claims: list[UnverifiedClaim]


def verify_section(section_text: str, context: str) -> list[UnverifiedClaim]:
    """Check every specific factual claim in a memo section against the context it was supposed to be grounded in."""
    prompt = (
        "You are fact-checking a section of a financial memo. Below is the section text, "
        "followed by the source context it was supposed to be grounded in. List every specific "
        "factual claim in the section (a number, date, statistic, or named fact) that is NOT "
        "directly supported by the source context -- do not flag general business language, only "
        "concrete factual claims. If everything is supported, return an empty list.\n\n"
        f"Section text:\n{section_text}\n\n"
        f"Source context:\n{context}"
    )
    response = client.with_options(timeout=900.0).messages.parse(
        model=MODEL,
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}],
        output_format=VerificationResult,
    )
    return response.parsed_output.unverified_claims


NUMBER_PATTERN = re.compile(r"\$?-?\d[\d,]*\.?\d*(?:\s?(?:thousand|million|billion))?%?", re.IGNORECASE)
UNIT_MULTIPLIERS = {"thousand": 1_000, "million": 1_000_000, "billion": 1_000_000_000}


def _parse_numeric_claim(token: str) -> tuple[float, bool] | None:
    """Parse a matched token into (canonical_value, is_percent), scaling million/billion/thousand to a common base."""
    is_percent = token.rstrip().endswith("%")
    lower = token.lower()
    multiplier = next((factor for unit, factor in UNIT_MULTIPLIERS.items() if unit in lower), 1)

    digits = re.sub(r"[^\d.\-]", "", token)
    if not digits or digits in {"-", "."}:
        return None
    # A bare single digit with no currency/unit/percent is almost always structural (list numbering, "3 pillars").
    if multiplier == 1 and not is_percent and len(digits.replace(".", "").replace("-", "")) <= 1:
        return None
    return float(digits) * multiplier, is_percent


def find_numeric_claims(text: str) -> set[tuple[float, bool]]:
    """Extract every numeric claim (dollar amount, percentage, plain number) from text as (value, is_percent) pairs."""
    claims = (_parse_numeric_claim(token) for token in NUMBER_PATTERN.findall(text))
    return {claim for claim in claims if claim is not None}


def verify_numbers_in_context(
    section_text: str, context: str, rel_tol: float = 0.01, percent_tol: float = 0.15
) -> list[str]:
    """Flag every numeric claim in section_text with no approximate match in context, after unit scaling.

    A small tolerance accounts for legitimate rounding differences (e.g. a filing's "$1,324,144 thousand"
    vs. prose's "$1,324.1 million" -- the same fact, rounded for readability).
    """
    claimed = find_numeric_claims(section_text)
    available = find_numeric_claims(context)

    unmatched = []
    for value, is_percent in claimed:
        tolerance = percent_tol if is_percent else abs(value) * rel_tol
        match_found = any(
            avail_is_percent == is_percent and abs(avail_value - value) <= tolerance
            for avail_value, avail_is_percent in available
        )
        if not match_found:
            unmatched.append(f"{value}{'%' if is_percent else ''}")
    return sorted(unmatched)


def generate_memo(business_context: str) -> str:
    """Generate a full memo, one section at a time, grounded in the extracted knowledge base and business context."""
    facts = load_category_facts("3 - Accounts")
    facts_context = json.dumps(facts, indent=2)

    parts = ["# Planet Fitness, Inc. -- Confidential Information Memorandum\n"]
    for name, instructions in SECTIONS:
        context = f"Structured facts:\n{facts_context}\n\nBusiness context:\n{business_context}"
        section_text = generate_section(name, instructions, context)
        parts.append(f"## {name}\n\n{section_text}\n")

        unverified = verify_section(section_text, context)
        if unverified:
            print(f"  [{name}] {len(unverified)} unverified claim(s) (semantic check):")
            for issue in unverified:
                print(f"    - {issue.claim} ({issue.reason})")

        unmatched_numbers = verify_numbers_in_context(section_text, context)
        if unmatched_numbers:
            print(f"  [{name}] {len(unmatched_numbers)} number(s) not found in source (strict check):")
            for number in unmatched_numbers:
                print(f"    - {number}")
    return "\n".join(parts)
