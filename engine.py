"""Small deterministic forward-chaining inference engine, independent of the UI."""
from knowledge_base import QUESTIONS, QUESTION_MAP, RULES, condition_text


def validate_answers(answers):
    """Reject malformed inputs; omitted observations remain unknown, never false."""
    if not isinstance(answers, dict):
        raise ValueError("Answers must be a JSON object.")
    if set(answers) - set(QUESTION_MAP):
        raise ValueError("Unknown answer field. Derived facts cannot be supplied by the user.")
    facts = {}
    for q in QUESTIONS:
        value = answers.get(q["key"], "unknown")
        if not isinstance(value, str) or value not in dict(q["choices"]):
            raise ValueError(f'Invalid choice for {q["key"]}.')
        facts[q["key"]] = value
    return facts


def infer(answers):
    facts = validate_answers(answers)
    fired = set()
    trace = []
    round_number = 0
    while True:
        # Use a snapshot: a fact derived in one round is consumed next round.
        eligible = [r for r in RULES if r["id"] not in fired
                    and all(facts.get(k) == v for k, v in r["all"])
                    and (not r["any"] or any(facts.get(k) == v for k, v in r["any"]))]
        if not eligible:
            break
        round_number += 1
        new_facts = {}
        for r in eligible:
            evidence = [c for c in r["all"] + r["any"] if facts.get(c[0]) == c[1]]
            parents = [t["rule_id"] for t in trace if t["rule_id"] in {"R14", "R15", "R16", "R17", "R18", "R19"}] if r["id"] == "R20" else []
            trace.append({"rule_id": r["id"], "round": round_number, "title": r["title"],
                          "kind": r["kind"], "advice": r["advice"], "evidence": [condition_text(c) for c in evidence],
                          "parents": parents, "sources": r["sources"], "source_section": r["source_section"],
                          "derived": dict(r["derive"])})
            fired.add(r["id"])
            new_facts.update(r["derive"])
        facts.update(new_facts)
    answered = sum(facts[q["key"]] != "unknown" for q in QUESTIONS)
    status = "matched" if trace else ("insufficient_information" if answered == 0 else "no_match")
    return {"status": status, "answered": answered, "question_count": len(QUESTIONS),
            "rounds": round_number, "trace": trace, "facts": facts,
            "message": ("Review the possible problems and care actions below." if trace else
                        "No conclusion from these answers. Check unknown observations or consult a plant specialist; this does not confirm that the plant is healthy.")}
