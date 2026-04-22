from flask import Flask, request, jsonify
from groq import Groq
import os
import re

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def strip_to_answer(text):
    # Remove common filler phrases the LLM adds
    text = re.sub(
        r'^(the final (answer|result|output) is[:\s]*|therefore[,\s]*|so[,\s]*|output[:\s]*|answer[:\s]*)',
        '', text.strip(), flags=re.IGNORECASE
    ).strip()
    # Remove surrounding quotes
    text = text.strip('"\'""')
    # If multiple lines, take last non-empty line
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
                "Work through this problem step by step. "
                "Execute every rule in strict order. "
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
                "You extract the final answer from reasoning. "
                "Return ONLY the final value — one word or one number. "
                "No sentences. No explanation. No punctuation. Just the value."
            )},
            {"role": "user", "content": query},
            {"role": "assistant", "content": chain},
            {"role": "user", "content": "Final answer only. One word or number:"}
        ]
    )

    raw = extraction.choices[0].message.content.strip()
    answer = strip_to_answer(raw)
    return jsonify({"output": answer}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)