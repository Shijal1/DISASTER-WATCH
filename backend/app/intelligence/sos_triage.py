"""
Algorithm 1 — Lexicon-based SOS severity triage.
Descended from CrisisLex-style curated vocabularies (Olteanu et al., 2014).
"""
import re
from typing import Optional


HIGH_TERMS = {
    "trapped", "bleeding", "collapse", "collapsed", "fire", "burning",
    "drowning", "drowned", "injured", "critical", "unconscious",
    "buried", "suffocating", "emergency", "dying", "dead", "severe",
    "attack", "explosion", "heart", "stroke", "urgent",
}

MODERATE_TERMS = {
    "food", "water", "shelter", "hungry", "thirsty", "stranded",
    "stuck", "isolated", "cut", "evacuation", "evacuate", "help",
    "medicine", "medical", "sick", "elderly", "children", "infant",
}

LOCATION_MARKERS = {"at", "near", "in", "on", "beside", "behind", "opposite"}

W_HIGH = 2
W_MOD = 1

PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)
TOKEN_RE = re.compile(r"\w+")


def _normalise(text: str) -> str:
    return PUNCT_RE.sub(" ", text.lower()).strip()


def _tokenise(text: str) -> list[str]:
    words = TOKEN_RE.findall(text)
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]
    return words + bigrams


def _extract_location(text: str) -> Optional[str]:
    """Return the phrase following the first location marker."""
    words = text.split()
    for i, w in enumerate(words):
        if w.lower() in LOCATION_MARKERS and i + 1 < len(words):
            return " ".join(words[i + 1 : i + 5])  # up to 4 words after marker
    return None


def classify(text: str) -> dict:
    """
    Returns:
      {
        "severity": "CRITICAL" | "MODERATE" | "LOW",
        "matched_evidence": [terms],
        "candidate_location": str | None
      }
    """
    normalised = _normalise(text)
    tokens = _tokenise(normalised)

    high_hits = sorted({t for t in tokens if t in HIGH_TERMS})
    mod_hits = sorted({t for t in tokens if t in MODERATE_TERMS})

    score = W_HIGH * len(high_hits) + W_MOD * len(mod_hits)

    if high_hits:
        severity = "CRITICAL"
    elif mod_hits:
        severity = "MODERATE"
    else:
        severity = "LOW"

    return {
        "severity": severity,
        "matched_evidence": high_hits + mod_hits,
        "candidate_location": _extract_location(text),
        "score": score,
    }