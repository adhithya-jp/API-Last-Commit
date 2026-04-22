from flask import Flask, request, jsonify
from groq import Groq
import os

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def solve():
    if request.method == "GET":
        return "API is running", 200

    data = request.get_json(silent=True) or {}
    query = str(data.get("query", ""))

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Answer math questions with exactly this format: 'The sum is X.' for addition, 'The difference is X.' for subtraction, 'The product is X.' for multiplication, 'The quotient is X.' for division. Use numbers not words. One sentence only. No markdown, no extra text."},
            {"role": "user", "content": query}
        ]
    )

    return jsonify({"output": response.choices[0].message.content.strip()}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)