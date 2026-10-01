from negotiation import negotiate


agent_x = {
    "claim": "YES",
    "evidence": [
        "CSE lab is scheduled at 3 PM"
    ],
    "confidence": 0.8
}


agent_y = {
    "claim": "NO",
    "evidence": [
        "Math class is scheduled from 2:30 PM to 3:30 PM"
    ],
    "confidence": 0.9
}


result = negotiate(agent_x, agent_y)


print("========== NEGOTIATION RESULT ==========")
print("Consensus:", result["consensus"])
print("Truth:", result["truth"])
print("Reason:", result["reason"])
print("Rounds:", result["rounds"])

print("\nNegotiation:")
for step in result["negotiation"]:
    print("-", step)