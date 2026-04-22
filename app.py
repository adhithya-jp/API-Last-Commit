from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/", methods=["GET", "POST"])
def solve():
    if request.method == "GET":
        return "API is running", 200

    data = request.get_json(silent=True) or {}
    query = str(data.get("query", ""))

    response = model.generate_content(
        f"Answer this question in one short sentence only. No extra text, no markdown:\n{query}"
    )

    return jsonify({"output": response.text.strip()}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  