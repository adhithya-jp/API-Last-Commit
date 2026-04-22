from flask import Flask, request, jsonify
from groq import Groq
import os
import re

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def try_solve(query):
    q = query.lower()
    
    # Extract numbers from query
    nums = list(map(int, re.findall(r'-?\d+', query)))
    
    # Sum even numbers
    if "sum even" in q or "add even" in q:
        return str(sum(n for n in nums if n % 2 == 0))
    
    # Sum odd numbers
    if "sum odd" in q or "add odd" in q:
        return str(sum(n for n in nums if n % 2 != 0))
    
    # Count even
    if "count even" in q:
        return str(len([n for n in nums if n % 2 == 0]))
    
    # Count odd
    if "count odd" in q:
        return str(len([n for n in nums if n % 2 != 0]))
    
    # Max
    if "max" in q or "largest" in q or "greatest" in q:
        return str(max(nums))
    
    # Min
    if "min" in q or "smallest" in q:
        return str(min(nums))
    
    # Sum all
    if "sum" in q or "total" in q or "add" in q:
        return str(sum(nums))
    
    return None

@app.route("/", methods=["GET", "POST"])
def solve():
    if request.method == "GET":
        return "API is running", 200

    data = request.get_json(silent=True) or {}
    query = str(data.get("query", ""))

    # Try deterministic first
    result = try_solve(query)
    if result:
        return jsonify({"output": result}), 200

    # Fallback to LLM
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Answer with only the final answer value. No explanation, no extra text. Just the number or word."},
            {"role": "user", "content": query}
        ]
    )
    return jsonify({"output": response.choices[0].message.content.strip()}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)