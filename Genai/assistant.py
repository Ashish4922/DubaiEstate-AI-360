
from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import pandas as pd

from Genai import retrieval
from Genai.prompts import (
    DISCLAIMER,
    SYSTEM_PROMPT,
    build_answer_prompt,
    build_refusal_prompt,
    format_verified_result,
)

logger = logging.getLogger(__name__)


class UnsupportedQuestion(Exception):
    """Raised when a question cannot be answered from the dataset."""


@dataclass
class Answer:
    question: str
    route: str  # tool name, or "refusal"
    text: str
    result: dict | None
    prompt: str  # what an LLM would be given (not sent anywhere)


# Safety checks (run before any tool is chosen)
# Each entry: (pattern, reason shown to the user)
BLOCKED_PATTERNS = [
    (
        r"ignore (all |any |the )?(previous|above|prior)|disregard|system prompt|you are now|pretend",
        "The question tries to change how the assistant works, so it was not followed.",
    ),
    (
        r"\bshould i\b|\bbuy\b|\binvest\w*|\brecommend\w*|good investment",
        "The assistant does not give buy, sell or investment advice.",
    ),
    (
        r"\bwill\b|\bforecast\w*|\bpredict\w*|\bfuture\b|next (year|month|quarter)|\bappreciat\w*",
        "The dataset holds past transactions only, so it cannot support predictions.",
    ),
    (
        r"\brent\w*|\byield\b|\broi\b|\boccupan\w*|\btenan\w*|\bmaintenance\b|\bmortgage\b",
        "The dataset has no rent, yield, occupancy, tenancy or maintenance data.",
    ),
]


def _blocked_reason(question: str) -> str | None:
    lowered = question.lower()
    for pattern, reason in BLOCKED_PATTERNS:
        if re.search(pattern, lowered):
            return reason
    return None


# Reading the question

SUBTYPES = {"flat": "Flat", "villa": "Villa", "office": "Office", "shop": "Shop"}
GENERIC_PLACES = {"dubai", "total", "general", "all", "all areas", "the dataset"}


def find_areas(question: str, area_names: list[str]) -> list[str]:
    """Return known area names mentioned in the question, in the order written.

    Longer names are matched first and blanked out, so 'Jabal Ali First'
    is not also counted as a shorter name inside it.
    """
    text = question.lower()
    found = []
    for name in sorted(area_names, key=len, reverse=True):
        match = re.search(rf"\b{re.escape(name.lower())}\b", text)
        if match:
            found.append((match.start(), name))
            text = text[: match.start()] + " " * len(name) + text[match.end():]
    return [name for _, name in sorted(found)]


def _find_subtype(question: str) -> str | None:
    for word, subtype in SUBTYPES.items():
        if re.search(rf"\b{word}s?\b", question.lower()):
            return subtype
    return None


def _guess_area(question: str) -> str | None:
    """Pick up an area name that is not in the data, e.g. 'flats in Atlantis'.

    Without this, an unknown area would be ignored and the assistant would
    quietly answer for the whole dataset, which would be misleading.
    """
    match = re.search(r"^.*\b(?:in|for|at)\s+(.+?)\s*[?.!]*$", question, re.I | re.S)
    if not match:
        return None
    candidate = match.group(1).strip()
    lowered = candidate.lower()
    if re.search(r"\d", candidate) or lowered in GENERIC_PLACES:
        return None
    if re.fullmatch(r"(flat|villa|office|shop)s?", lowered):
        return None
    return candidate


def _parse_between(question: str) -> tuple[str, str] | None:
    match = re.search(r"between\s+(.+?)\s+and\s+(.+?)\s*[?.!]*$", question, re.I)
    return (match.group(1).strip(), match.group(2).strip()) if match else None


# Tool selection

def _route(df: pd.DataFrame, question: str) -> tuple[str, dict]:
    """Choose a retrieval tool and run it. Raises UnsupportedQuestion."""
    q = question.lower()
    areas = find_areas(question, df["AREA_EN"].dropna().unique().tolist())

    if re.search(r"\bmonth(s|ly)?\b", q):
        return "monthly_sales_count", retrieval.monthly_sales_count(df)

    if re.search(r"off[- ]?plan|\bready\b", q):
        return "offplan_share", retrieval.offplan_share(df)

    wants_sqm = bool(re.search(r"per (sq|square)|\bsqm\b|sq\.? ?m\b|square met", q))
    wants_compare = bool(re.search(r"\bcompare|\bbetween\b|\bvs\.?\b|\bversus\b", q))

    if wants_compare and (wants_sqm or len(areas) >= 2):
        pair = tuple(areas[:2]) if len(areas) >= 2 else _parse_between(question)
        if pair is None:
            raise UnsupportedQuestion(
                "A comparison needs two areas, for example 'between Area X and Area Y'."
            )
        return "compare_price_per_sqm", retrieval.compare_price_per_sqm(df, *pair)

    if re.search(r"\btop\b|busiest|most (sales|transactions)", q):
        if re.search(r"price|value|cost|expensive", q):
            raise UnsupportedQuestion(
                "Ranking areas by price is not supported yet. Ranking by number of sales is."
            )
        match = re.search(r"\btop (\d+)\b", q)
        n = min(max(int(match.group(1)), 1), 20) if match else 5
        return "top_areas_by_count", retrieval.top_areas_by_count(df, n)

    if wants_sqm:
        area = areas[0] if areas else _guess_area(question)
        return "median_price_per_sqm", retrieval.median_price_per_sqm(df, area)

    if re.search(r"median|average|\bmean\b|typical|price|value|cost", q):
        area = areas[0] if areas else _guess_area(question)
        return "median_sale_value", retrieval.median_sale_value(
            df, area=area, subtype=_find_subtype(question)
        )

    raise UnsupportedQuestion("The question does not match any calculation the assistant supports.")


# Writing the answer

def _figure_lines(result: dict) -> list[str]:
    metric, value = result["metric"], result["value"]

    if value is None:
        return ["No figure can be given for this question."]
    if metric == "median_sale_value":
        return [f"The median sale value is AED {value:,.0f}."]
    if metric == "median_price_per_sqm":
        return [f"The median price is AED {value:,.0f} per sq m."]
    if metric == "compare_price_per_sqm":
        lines = ["Median price per sq m (units only):"]
        for area, figure in value.items():
            text = f"AED {figure:,.0f} per sq m" if figure is not None else "no figure"
            lines.append(f"  - {area}: {text}")
        return lines
    if metric == "monthly_sales_count":
        return ["Sales transactions per month:"] + [f"  - {m}: {n:,}" for m, n in value.items()]
    if metric.startswith("top_"):
        lines = ["Areas ranked by number of sales transactions:"]
        return lines + [f"  {i}. {a}: {n:,}" for i, (a, n) in enumerate(value.items(), 1)]
    if metric == "offplan_share":
        lines = ["Share of sales by status:"]
        return lines + [
            f"  - {status}: {v['count']:,} sales ({v['percent']}%)" for status, v in value.items()
        ]
    return [str(value)]


def _render(result: dict, question: str) -> str:
    size = result["sample_size"]
    if isinstance(size, dict):
        size = ", ".join(f"{area}: {n:,}" for area, n in size.items())
    else:
        size = f"{size:,}"

    lines = _figure_lines(result)
    if re.search(r"average|\bmean\b", question.lower()) and result["metric"].startswith("median"):
        lines.append("Note: the median is reported instead of the average because it is less "
                     "affected by a few very large or very small sales.")

    lines += [
        "",
        f"Filters: {result['filters']}",
        f"Sample size: {size}",
        f"Date coverage: {result['date_coverage']}",
    ]
    if result["warnings"] != "none":
        lines.append(f"Warnings: {result['warnings']}")
    lines += [
        "Uncertainty: these figures describe recorded transactions only and "
        "say nothing about future prices.",
        DISCLAIMER,
    ]
    return "\n".join(lines)


def _refuse(question: str, reason: str) -> Answer:
    text = (
        f"I can't answer that from this dataset. {reason}\n"
        "Try something like: 'What is the median price per sq m in <area>?' "
        "or 'Which are the top 5 areas by number of sales?'\n"
        f"{DISCLAIMER}"
    )
    prompt = SYSTEM_PROMPT + "\n" + build_refusal_prompt(question or "(empty)", reason)
    return Answer(question, "refusal", text, None, prompt)


# Public entry point

def answer_question(df: pd.DataFrame, question: str) -> Answer:
    """Answer one question using verified dataset figures only."""
    question = (question or "").strip()
    if not question:
        return _refuse(question, "No question was entered.")

    reason = _blocked_reason(question)
    if reason:
        logger.info("Refused (safety rule): %s", question)
        return _refuse(question, reason)

    try:
        route, result = _route(df, question)
    except UnsupportedQuestion as error:
        logger.info("Refused (unsupported): %s", question)
        return _refuse(question, str(error))

    logger.info("Question routed to %s", route)
    prompt = SYSTEM_PROMPT + "\n" + build_answer_prompt(question, format_verified_result(result))
    return Answer(question, route, _render(result, question), result, prompt)
