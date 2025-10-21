def parse_intent(text):
    """
    for now this is a functionting prototype. 

    later ollama will handle the parsing thing and return the dictionary -> {action: $ACTION, target: $TARGET}

    """
    text_lower = text.lower()
    if text_lower.startswith("run") or text_lower.endswith(".sh") or text_lower.endswith(".py"):
        target = text_lower.split()[-1]
        return {"action": "run_scripts", "target": target}

    # if "ref" in text_lower:
    #     return {"intent": "ref", "target": None}

    # if "export" in text_lower:
    #     return {"intent": "export", "target": None}
    return {"action": None, "target": None}

