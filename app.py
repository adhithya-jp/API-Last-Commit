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
        temperature=0,
        messages=[
            {"role": "system", "content": (
                "You are a universal answer engine. Detect the task type and respond accordingly:\n\n"
                "MATH (addition/subtraction/multiply/divide): Respond 'The sum/difference/product/quotient is X.'\n"
                "YES/NO QUESTIONS: Respond with only YES or NO in uppercase\n"
                "EXTRACTION (date, name, email, number, etc): Return ONLY the extracted value, nothing else\n"
                "LIST OPERATIONS (sum even/odd, max, min, count, sort, filter): Return ONLY the final result\n"
                "SORTING: Return the sorted list as comma-separated values\n"
                "COUNTING: Return just the number\n"
                "COMPARISON: Return the answer directly\n"
                "GENERAL KNOWLEDGE: One sentence, direct answer only\n\n"
                "GLOBAL RULES: No explanation. No markdown. No extra words. No punctuation unless part of the answer."
            )},
            {"role": "user", "content": query}
        ]
    )
    return jsonify({"output": response.choices[0].message.content.strip()}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)