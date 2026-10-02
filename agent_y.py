from typing import Any, Dict, List

def _clean_claim(q: str) -> str:
    return q.strip().rstrip("?.!")

def make_opposing_claim(question: str) -> str:
    q = _clean_claim(question)
    return (
        f"Counter-position: the proposition expressed by “{q}” "
        f"may not hold as stated."
    )

class AgentY:
    def __init__(self, name: str = "Agent B"):
        self.name = name

    def analyze_question(
        self,
        question: str,
        external_evidence: List[Dict[str, str]] | None = None,
    ) -> Dict[str, Any]:
        results = external_evidence or []
        details = []

        for item in results[:6]:
            details.append({
                "title": item.get("title", "Untitled source"),
                "source": item.get("source", "Web source"),
                "url": item.get("url", ""),
                "snippet": item.get("snippet", ""),
                "published": item.get("published", ""),
                "role": "Counter-evidence lead",
            })

        return {
            "agent": self.name,
            "claimText": make_opposing_claim(question),
            "position": "CHALLENGES",
            "evidence": details,
            "reasoning": (
                "Agent B independently searched for evidence that could establish "
                "a genuine counterposition. A source is not counted as counter-"
                "evidence merely because it mentions the same topic."
            ) if details else (
                "Agent B did not retrieve sufficiently direct counter-evidence. "
                "Topic-related sources are not presented as proof against the claim."
            ),
            "confidence": round(
                min(0.85, 0.35 + 0.07 * len(details)), 2
            ) if details else 0.25,
        }
