from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def solve():
    if request.method == "GET":
        return "API is running", 200

    try:
        data = request.get_json(silent=True) or {}
        query = str(data.get("query", ""))

        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(
            f"Answer this question in one short sentence only. No extra text, no markdown, no asterisks:\n{query}"
        )

        answer = response.candidates[0].content.parts[0].text.strip()
        return jsonify({"output": answer}), 200

    except Exception as e:
        return jsonify({"output": str(e)}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)