from flask import Flask, request, jsonify
from groq import Groq
import os
import re

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def strip_to_answer(text):
    text = re.sub(
        r'^(the final (answer|result|output) is[:\s]*|therefore[,\s]*|so[,\s]*|output[:\s]*|answer[:\s]*)',
        '', text.strip(), flags=re.IGNORECASE
    ).strip()
    text = text.strip('"\'"\u201c\u201d')
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return lines[-1] if lines else text

def solve_math(query):
    q = query.lower()

    # Modular arithmetic: X^Y mod Z
    m = re.search(r'(\d+)\s*[\^]\s*(\d+)\s*mod\s*10\^(\d+)', query, re.IGNORECASE)
    if m:
        base, exp, digits = int(m.group(1)), int(m.group(2)), int(m.group(3))
        result = pow(base, exp, 10**digits)
        return str(result)

    # Last N digits of X^Y
    m = re.search(r'last\s*(\d+)\s*digits?\s*of\s*(\d+)\s*[\^]\s*(\d+)', q)
    if m:
        digits, base, exp = int(m.group(1)), int(m.group(2)), int(m.group(3))
        result = pow(base, exp, 10**digits)
        return str(result)

    return None

def needs_reasoning(query):
    q = query.lower()
    return any(k in q for k in [
        "rule 1", "rule 2", "apply rule", "if even", "if odd",
        "if result", "divisible by", "apply the following",
        "transaction log", "filter", "extract the first",
        "pipe-separated", "verified", "unverified", "disputed"
    ])

def single_call(query):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {"role": "system", "content": (
                "You are a precise answer engine. Return ONLY the final answer.\n\n"
                "MATH/KNOWLEDGE: return just the number or fact\n"
                "YES/NO: YES or NO in uppercase\n"
                "EXTRACTION: only the extracted value\n"
                "LIST OPS: only the final number or list\n"
                "COMPARISON: only the name, original capitalisation\n"
                "FORMATTING: follow exact format specified\n\n"
                "No explanation. No markdown. No extra words. One line only."
            )},
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message.content.strip()

def two_step_call(query):
    reasoning = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {"role": "system", "content": (
                "You are a precise reasoning engine. Work through the problem step by step.\n"
                "For rule execution: apply every rule in strict order, use each result as input to next.\n"
                "For data filtering: parse carefully, apply ALL conditions, return FIRST match unless told otherwise.\n"
                "For transaction results use: '[Name] paid the amount of $[amount].'\n"
                "For label-priority: always trust [VERIFIED] over [UNVERIFIED] or [DISPUTED].\n"
                "For formatting: follow the exact format specified.\n"
                "Show all working clearly."
            )},
            {"role": "user", "content": query}
        ]
    )
    chain = reasoning.choices[0].message.content.strip()

    extraction = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {"role": "system", "content": (
                "Extract the final answer from the reasoning.\n"
                "Return ONLY the final answer. No explanation. No markdown. Just the answer."
            )},
            {"role": "user",      "content": query},
            {"role": "assistant", "content": chain},
            {"role": "user",      "content": "Final answer only:"}
        ]
    )
    return extraction.choices[0].message.content.strip()

@app.route("/", methods=["GET", "POST"])
def solve():
    if request.method == "GET":
        return "API is running", 200

    data  = request.get_json(silent=True) or {}
    query = str(data.get("query", ""))

    # 1. Deterministic math solver (exact, instant)
    result = solve_math(query)
    if result:
        return jsonify({"output": result}), 200

    # 2. Two-step reasoning for complex rule/filter tasks
    if needs_reasoning(query):
        raw = two_step_call(query)
    else:
        raw = single_call(query)

    answer = strip_to_answer(raw)
    return jsonify({"output": answer}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)