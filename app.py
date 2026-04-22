from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def solve():
    if request.method == "GET":
        return "API is running", 200

    data = request.get_json(force=True) or {}
    query = str(data.get("query", ""))

    nums = list(map(int, re.findall(r"-?\d+", query)))
    total = sum(nums)

    return jsonify({"output": f"The sum is {total}."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)