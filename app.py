from flask import Flask, request, jsonify
from groq import Groq
import os
import re

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def try_solve(query):
    q = query.lower()
    nums = list(map(int, re.findall(r'-?\d+', query)))

    if "sum even" in q or "add even" in q:
        return str(sum(n for n in nums if n % 2 == 0))
    if "sum odd" in q or "add odd" in q:
        return str(sum(n for n in nums if n % 2 != 0))
    if "count even" in q:
        return str(len([n for n in nums if n % 2 == 0]))
    if "count odd" in q:
        return str(len([n for n in nums if n % 2 != 0]))
    if "max" in q or "largest" in q or "greatest" in q:
        return str(max(nums)) if nums else None
    if "min" in q or "smallest" in q:
        return str(min(nums)) if nums else None
    if "total" in q:
        return str(sum(nums)) if nums else None

    return None

@app.route("/", methods=["GET", "POST"])
def solve():
    if request.method == "GET":
        return "API is running", 200

    data = request.get_json(silent=True) or {}
    query = str(data.get("query", ""))

    result = try_solve(query)
    if result:
        return jsonify({"output": result}), 200

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        messages=[
            {"role": "system", "content": "Return ONLY the answer. No explanation. For addition questions use format 'The sum is X.' For subtraction use 'The difference is X.' For multiplication use 'The product is X.' For division use 'The quotient is X.' For yes/no questions return YES or NO in caps. For extraction return just the extracted value. For number operations like sum/count/max/min return just the number."},
            {"role": "user", "content": query}
        ]
    )
    return jsonify({"output": response.choices[0].message.content.strip()}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)