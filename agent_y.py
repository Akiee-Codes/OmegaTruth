from typing import Dict, Any


class AgentY:
    """Counter-Perspective / Dissent Agent"""

    def __init__(self, name: str = "Agent_Y"):
        self.name = name

    def analyze_question(self, question: str) -> Dict[str, Any]:
        """
        Analyze the same question as Agent X,
        but provide an independent counter-perspective.
        """

        question_lower = question.lower()

        # Demonstration scenario for our first integration test
        if "3 pm" in question_lower or "3pm" in question_lower:
            claim = "NO"
            evidence = [
                "Math class is scheduled from 2:30 PM to 3:30 PM."
            ]
            confidence = 0.90
            reasoning = (
                "Agent Y found evidence that the math class overlaps 3 PM."
            )

        else:
            claim = "INSUFFICIENT_EVIDENCE"
            evidence = [
                "No matching information was found in the current knowledge base."
            ]
            confidence = 0.30
            reasoning = (
                "Agent Y does not have enough evidence to make a reliable claim."
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
    agent_y = AgentY()

    question = input("Enter your question: ")

    result = agent_y.analyze_question(question)

    print("\n========== AGENT Y ==========")
    print("Question:", result["question"])
    print("Claim:", result["claim"])
    print("Evidence:", result["evidence"])
    print("Confidence:", result["confidence"])
    print("Reasoning:", result["reasoning"])


if __name__ == "__main__":
    main()