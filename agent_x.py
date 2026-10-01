from typing import Dict, Any


class AgentX:
    """Initial Proposal Agent"""

    def __init__(self, name: str = "Agent_X"):
        self.name = name

    def analyze_question(self, question: str) -> Dict[str, Any]:
        """
        Analyze the user's question and produce an initial claim,
        evidence, confidence, and reasoning.
        """

        # Simple demonstration knowledge base.
        # We will make this dynamic later.
        question_lower = question.lower()

        if "3 pm" in question_lower or "3pm" in question_lower:
            claim = "YES"
            evidence = [
                "CSE lab is scheduled at 3 PM."
            ]
            confidence = 0.80
            reasoning = (
                "Agent X found evidence that the CSE lab is scheduled at 3 PM."
            )

        else:
            claim = "INSUFFICIENT_EVIDENCE"
            evidence = [
                "No matching information was found in the current knowledge base."
            ]
            confidence = 0.30
            reasoning = (
                "Agent X does not have enough evidence to make a reliable claim."
            )

        return {
            "agent": self.name,
            "question": question,
            "claim": claim,
            "evidence": evidence,
            "confidence": confidence,
            "reasoning": reasoning
        }


def main():
    agent_x = AgentX()

    question = input("Enter your question: ")

    result = agent_x.analyze_question(question)

    print("\n========== AGENT X ==========")
    print("Question:", result["question"])
    print("Claim:", result["claim"])
    print("Evidence:", result["evidence"])
    print("Confidence:", result["confidence"])
    print("Reasoning:", result["reasoning"])


if __name__ == "__main__":
    main()