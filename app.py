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

@app.route("/", methods=["GET", "POST"])
def solve():
    if request.method == "GET":
        return "API is running", 200

    data  = request.get_json(silent=True) or {}
    query = str(data.get("query", ""))

    # Step 1: full reasoning
    reasoning = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {"role": "system", "content": (
                "You are a precise reasoning engine. Work through the problem step by step.\n"
                "For rule execution: apply every rule in strict order, use each result as input to next.\n"
                "For data filtering/extraction tasks (transaction logs, records, lists):\n"
                "  - Parse each entry carefully\n"
                "  - Apply ALL filter conditions\n"
                "  - Return the FIRST match unless told otherwise\n"
                "  - Use this sentence format for transaction results: '[Name] paid the amount of $[amount].'\n"
                "For label-priority tasks: always trust [VERIFIED] over [UNVERIFIED] or [DISPUTED].\n"
                "For formatting tasks: follow the exact format specified in the query.\n"
                "Show all working clearly."
            )},
            {"role": "user", "content": query}
        ]
    )
    chain = reasoning.choices[0].message.content.strip()

    # Step 2: extract final answer only
    extraction = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {"role": "system", "content": (
                "Extract the final answer from the reasoning provided.\n"
                "Return ONLY the final answer — one value, one sentence, or one formatted result.\n"
                "No explanation. No extra words. No markdown. Just the answer."
            )},
            {"role": "user",      "content": query},
            {"role": "assistant", "content": chain},
            {"role": "user",      "content": "Final answer only:"}
        ]
    )

    raw    = extraction.choices[0].message.content.strip()
    answer = strip_to_answer(raw)
    return jsonify({"output": answer}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)