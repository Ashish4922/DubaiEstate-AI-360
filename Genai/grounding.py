
from __future__ import annotations

import re

from Genai.assistant import Answer

NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
MONTH_LABEL = re.compile(r"\d{4}-\d{2}")
RANK_MARKER = re.compile(r"(?m)^\s*\d+\.\s")


def _collect(obj, numbers: set[float], names: set[str]) -> None:
    """Gather every number and every dictionary key found inside obj."""
    if obj is None or isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        numbers.add(round(float(obj), 2))
        numbers.add(float(round(obj)))
    elif isinstance(obj, dict):
        for key, value in obj.items():
            names.add(str(key))
            _collect(value, numbers, names)


def figure_block(answer: Answer) -> str:
    """The part of the answer text that states figures (before the first blank line)."""
    return answer.text.split("\n\n")[0]


def ungrounded_numbers(answer: Answer) -> list[float]:
    """Return numbers stated in the answer that are not in its verified result.

    Refusals carry no result and state no figures, so they return an empty list.
    """
    if answer.result is None:
        return []

    allowed: set[float] = set()
    names: set[str] = set()
    _collect(answer.result["value"], allowed, names)
    _collect(answer.result["sample_size"], allowed, names)

    text = figure_block(answer)
    for name in sorted(names, key=len, reverse=True):
        text = text.replace(name, " ")  # area names can contain digits
    text = MONTH_LABEL.sub(" ", text)
    text = RANK_MARKER.sub("", text)

    stated = {float(n.replace(",", "")) for n in NUMBER.findall(text)}
    return sorted(stated - allowed)