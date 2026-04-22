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
            {"role": "system", "content": (
                "You are a precise answer engine. Rules:\n"
                "- Return ONLY the final answer, nothing else\n"
                "- No explanation, no punctuation added, no extra words\n"
                "- Numbers: return just the number (e.g. 10)\n"
                "- Yes/No questions: return YES or NO in caps\n"
                "- Math: 'The sum is X.' / 'The difference is X.' / 'The product is X.' / 'The quotient is X.'\n"
                "- Extraction tasks: return just the extracted value\n"
                "- List operations (sum even, max, min, count): return just the number"
            )},
            {"role": "user", "content": query}
        ]
    )
    return jsonify({"output": response.choices[0].message.content.strip()}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)