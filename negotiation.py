def negotiate(agent_x, agent_y):
    """
    Negotiation engine for two agents.

    Each agent provides:
    - claim
    - evidence
    - confidence
    """

    # Round 0: Check whether both agents already agree
    if agent_x["claim"] == agent_y["claim"]:
        return {
            "consensus": True,
            "truth": agent_x["claim"],
            "reason": "Both agents agree.",
            "rounds": 0,
            "negotiation": [
                "Agent X and Agent Y started with the same claim."
            ]
        }

    # Round 1: Detect disagreement
    negotiation_log = [
        f"Agent X initially claimed: {agent_x['claim']}",
        f"Agent Y initially claimed: {agent_y['claim']}",
        "Disagreement detected."
    ]

    # Compare confidence
    if agent_x["confidence"] > agent_y["confidence"]:
        stronger_agent = "X"
        truth = agent_x["claim"]
    elif agent_y["confidence"] > agent_x["confidence"]:
        stronger_agent = "Y"
        truth = agent_y["claim"]
    else:
        stronger_agent = None
        truth = "UNRESOLVED"

    # Resolve if one agent has stronger evidence/confidence
    if stronger_agent:
        negotiation_log.append(
            f"Agent {stronger_agent} has stronger supporting evidence."
        )
        negotiation_log.append(
            f"Shared truth selected: {truth}"
        )

        return {
            "consensus": True,
            "truth": truth,
            "reason": f"Agent {stronger_agent} provided stronger supporting evidence.",
            "rounds": 1,
            "negotiation": negotiation_log
        }

    # No clear winner → do not force a decision
    negotiation_log.append(
        "Evidence strength is equal. More evidence is required."
    )

    return {
        "consensus": False,
        "truth": "UNRESOLVED",
        "reason": "Neither agent has stronger evidence.",
        "rounds": 1,
        "negotiation": negotiation_log
    }