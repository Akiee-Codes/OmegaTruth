from typing import Any, Dict, List
from urllib.parse import urlparse
import re

def _as_item(item: Any) -> Dict[str, Any]:
    if isinstance(item, dict):
        return item
    if isinstance(item, str):
        return {
            "title": item,
            "snippet": item,
            "url": "",
            "source": "Evidence lead",
        }
    return {}

def _key(item: Dict[str, Any]) -> str:
    item = _as_item(item)
    return (item.get("url") or item.get("title") or "").strip().lower()

def _source_weight(item: Dict[str, Any]) -> float:
    item = _as_item(item)
    url = (item.get("url") or "").lower()
    source = (item.get("source") or "").lower()
    host = urlparse(url).netloc.lower()
    score = 1.0

    if host.endswith(".gov") or ".gov." in host:
        score += 1.5
    if host.endswith(".edu") or ".ac." in host:
        score += 1.2
    if any(k in host for k in (
        "who.int", "nih.gov", "pubmed", "nature.com",
        "sciencedirect.com", "springer.com", "cochrane.org",
        "reuters.com", "apnews.com", "britannica.com"
    )):
        score += 1.2
    if "wikipedia.org" in host:
        score += 0.2
    if any(k in source for k in (
        "government", "university", "journal", "research",
        "reuters", "associated press", "britannica"
    )):
        score += 0.5
    return score

def _text(item: Dict[str, Any]) -> str:
    item = _as_item(item)
    return " ".join(
        str(item.get(k, "")) for k in ("title", "snippet", "source")
    ).lower()

def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))

_STOP = set("""
the a an is are was were be been being do does did can could should would will
may might must has have had to of in on for with and or but that this these
those it its as by from than into about after before whether how why what which
who their they them there here claim according to stated proposition not
necessarily
""".split())

def _claim_terms(question: str) -> set[str]:
    return {
        x for x in _tokens(question)
        if len(x) > 2 and x not in _STOP
    }

def _overlap(item: Dict[str, Any], question: str) -> float:
    terms = _claim_terms(question)
    if not terms:
        return 0.0
    return len(terms & _tokens(_text(item))) / len(terms)

_SUPPORT = (
    "study found", "studies found", "research found", "randomized trial",
    "clinical trial", "systematic review", "meta-analysis", "evidence suggests",
    "evidence shows", "evidence supports", "associated with", "improves",
    "improved", "improvement", "benefit", "benefits", "demonstrates",
    "demonstrated", "shows that", "showed that", "found that",
    "significant improvement", "significantly improved", "increased",
    "reduces", "reduced", "contains", "is composed", "consists of",
    "made up of", "chemical formula"
)

_COUNTER = (
    "no evidence", "lack of evidence", "insufficient evidence",
    "not supported", "unsupported", "does not improve", "doesn't improve",
    "did not improve", "didn't improve", "no significant improvement",
    "no significant difference", "no significant effect", "failed to improve",
    "failed to show", "not associated", "not linked", "not effective",
    "ineffective", "refuted", "disproves", "disproved", "debunked",
    "contradicts", "contradict", "false", "not true", "incorrect",
    "misleading", "cannot", "could not", "was not", "were not",
    "has not", "have not", "does not", "do not", "is not", "are not"
)

def _direction_strength(
    item: Dict[str, Any], side: str, question: str
) -> float:
    text = _text(item)
    overlap = _overlap(item, question)

    if overlap < 0.30:
        return 0.0

    if side == "counter":
        neg = sum(1 for marker in _COUNTER if marker in text)
        if neg == 0:
            return 0.0
        return min(
            1.0,
            0.30 + 0.45 * min(overlap, 1.0) + 0.10 * min(neg, 3),
        )

    hits = sum(1 for marker in _SUPPORT if marker in text)
    return min(
        1.0,
        0.25 + 0.55 * min(overlap, 1.0) + 0.08 * min(hits, 3),
    )

def _score(
    items: List[Dict[str, Any]],
    side: str,
    question: str,
) -> float:
    values = []
    hosts = set()

    for item in items:
        strength = _direction_strength(item, side, question)
        if strength <= 0:
            continue

        values.append(_source_weight(item) * strength)
        host = urlparse(
            (_as_item(item).get("url") or "")
        ).netloc.lower()
        if host:
            hosts.add(host)

    if not values:
        return 0.0

    return (
        sum(sorted(values, reverse=True)[:5])
        + min(len(hosts), 4) * 0.35
    )

def _direct(items, side, question):
    return [
        item for item in items
        if _direction_strength(item, side, question) >= 0.58
    ]

def _shared(agent_a_items, agent_b_items):
    a = {_key(x) for x in agent_a_items if _key(x)}
    b = {_key(x) for x in agent_b_items if _key(x)}
    return a & b

def _reassessment(question, ax, ay):
    a_direct = _direct(ax, "support", question)
    b_direct = _direct(ay, "counter", question)
    a_score = _score(ax, "support", question)
    b_score = _score(ay, "counter", question)
    claim = question.strip().rstrip("?.!")

    if not a_direct and not b_direct:
        status = "INSUFFICIENT EVIDENCE"
        reason = (
            f"The retrieved material did not contain a sufficiently direct "
            f"source supporting or contradicting “{claim}”. Topic-related "
            f"articles are not counted as proof."
        )
        revisions = [
            (
                "Agent A", "SUPPORTS", "UNRESOLVED",
                "No sufficiently direct supporting evidence was retrieved.",
            ),
            (
                "Agent B", "CHALLENGES", "UNRESOLVED",
                "No sufficiently direct counter-evidence was retrieved.",
            ),
        ]
        return status, reason, revisions, a_score, b_score

    if a_direct and not b_direct:
        status = "AGENT B ACCEPTS AGENT A'S CLAIM"
        reason = (
            "Agent A retrieved direct supporting evidence, while Agent B did "
            "not retrieve credible direct counter-evidence."
        )
        revisions = [
            (
                "Agent A", "SUPPORTS", "SUPPORTS WITH QUALIFICATION",
                "I retain the supporting view while acknowledging the limits "
                "of search-based evidence.",
            ),
            (
                "Agent B", "CHALLENGES", "ACCEPTS AGENT A'S CLAIM",
                "I change my viewpoint because my independent search did not "
                "produce direct evidence contradicting the claim.",
            ),
        ]
        return status, reason, revisions, a_score, b_score

    if b_direct and not a_direct:
        status = "AGENT A ACCEPTS AGENT B'S CLAIM"
        reason = (
            "Agent B retrieved direct counter-evidence, while Agent A did "
            "not retrieve comparably direct supporting evidence."
        )
        revisions = [
            (
                "Agent A", "SUPPORTS", "ACCEPTS AGENT B'S CLAIM",
                "I change my viewpoint because the retrieved counter-evidence "
                "directly challenges the original proposition.",
            ),
            (
                "Agent B", "CHALLENGES", "CHALLENGES WITH QUALIFICATION",
                "I retain the challenging view while acknowledging the limits "
                "of search-based evidence.",
            ),
        ]
        return status, reason, revisions, a_score, b_score

    gap = abs(a_score - b_score)
    scale = max(a_score, b_score, 1.0)

    if gap / scale <= 0.22:
        status = "PARTIAL MIDDLE GROUND"
        reason = (
            f"Both agents retrieved direct evidence relevant to “{claim}”, "
            "and their weighted evidence is sufficiently close that neither "
            "side has a clear basis to overturn the other."
        )
        revisions = [
            (
                "Agent A", "SUPPORTS", "QUALIFIED SUPPORT",
                "I accept relevant counter-evidence and narrow the original "
                "claim to reflect the evidence.",
            ),
            (
                "Agent B", "CHALLENGES", "QUALIFIED CHALLENGE",
                "I accept relevant supporting evidence and narrow the original "
                "counter-position.",
            ),
        ]
        return status, reason, revisions, a_score, b_score

    if a_score > b_score:
        status = "AGENT B ACCEPTS AGENT A'S CLAIM"
        reason = (
            "Both sides retrieved direct evidence, but Agent A's evidence "
            "has the stronger combined relevance, source-quality, and "
            "source-diversity score."
        )
        revisions = [
            (
                "Agent A", "SUPPORTS", "SUPPORTS WITH QUALIFICATION",
                "I retain the supporting view while acknowledging the "
                "counter-evidence.",
            ),
            (
                "Agent B", "CHALLENGES", "ACCEPTS AGENT A'S CLAIM",
                "I change my viewpoint because Agent A's direct evidence "
                "is materially stronger in the evidence comparison.",
            ),
        ]
    else:
        status = "AGENT A ACCEPTS AGENT B'S CLAIM"
        reason = (
            "Both sides retrieved direct evidence, but Agent B's evidence "
            "has the stronger combined relevance, source-quality, and "
            "source-diversity score."
        )
        revisions = [
            (
                "Agent A", "SUPPORTS", "ACCEPTS AGENT B'S CLAIM",
                "I change my viewpoint because the direct counter-evidence "
                "is materially stronger in the evidence comparison.",
            ),
            (
                "Agent B", "CHALLENGES", "CHALLENGES WITH QUALIFICATION",
                "I retain the challenging view while acknowledging the "
                "supporting evidence.",
            ),
        ]

    return status, reason, revisions, a_score, b_score

def negotiate(
    agent_x: Dict[str, Any],
    agent_y: Dict[str, Any],
    question: str = "the claim",
) -> Dict[str, Any]:
    ax = [_as_item(x) for x in (agent_x.get("evidence") or [])]
    ay = [_as_item(x) for x in (agent_y.get("evidence") or [])]

    shared = _shared(ax, ay)
    shared_set = set(shared)
    unique_a = [x for x in ax if _key(x) not in shared_set]
    unique_b = [x for x in ay if _key(x) not in shared_set]

    status, reason, revisions, a_score, b_score = _reassessment(
        question, ax, ay
    )

    trace = [
        "Both agents generated independent positions from the user's claim.",
        f"Agent A supplied {len(ax)} independent evidence lead(s); "
        f"{len(_direct(ax, 'support', question))} passed the direct-support test.",
        f"Agent B supplied {len(ay)} independent evidence lead(s); "
        f"{len(_direct(ay, 'counter', question))} passed the direct-counter test.",
        "The agents exchange their independently retrieved evidence.",
        "Topic relevance alone is not counted as proof or counter-proof.",
        f"Agent A reassesses: {revisions[0][2]}.",
        f"Agent B reassesses: {revisions[1][2]}.",
        f"Final resolution: {status}.",
    ]

    payload = [
        {
            "agent": name,
            "initial_position": initial,
            "revised_position": revised,
            "reason": explanation,
        }
        for name, initial, revised, explanation in revisions
    ]

    return {
        "status": status,
        "truth": status,
        "consensus": status != "INSUFFICIENT EVIDENCE",
        "reason": reason,
        "rounds": 2,
        "negotiation": trace,
        "revisions": payload,
        "evidence_exchange": {
            "agent_a_received": ay,
            "agent_b_received": ax,
        },
        "limitations": [
            "Search results are evidence leads, not independent fact verification.",
            "Topic relevance alone is not treated as proof or counter-proof.",
            "Directness is a transparent heuristic based on claim-term overlap, "
            "explicit support/contradiction language, source characteristics, "
            "and source diversity.",
            f"{len(shared)} source(s) appeared in both search sets; "
            f"{len(unique_a)} were unique to Agent A and "
            f"{len(unique_b)} were unique to Agent B.",
        ],
        "evidence_scores": {
            "agent_a": round(a_score, 2),
            "agent_b": round(b_score, 2),
        },
    }
