from typing import Any, Dict, List

def _clean_claim(q: str) -> str:
    return q.strip().rstrip("?.!")

def build_supporting_position(question: str) -> str:
    q = _clean_claim(question)
    return f"The proposition expressed by “{q}” is the position Agent A will test for supporting evidence."

class AgentX:
    def __init__(self, name: str = "Agent A"):
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
                "role": "Supporting evidence lead",
            })

        return {
            "agent": self.name,
            "claimText": build_supporting_position(question),
            "position": "SUPPORTS",
            "evidence": details,
            "reasoning": (
                "Agent A independently searched for sources that could support the "
                "original proposition. Search results are evidence leads, not proof "
                "by themselves."
            ) if details else (
                "Agent A did not retrieve sufficiently relevant supporting evidence "
                "from the public search channels."
            ),
            "confidence": round(
                min(0.90, 0.40 + 0.08 * len(details)), 2
            ) if details else 0.25,
        }
