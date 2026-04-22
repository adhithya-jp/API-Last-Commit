from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def solve():
    if request.method == "GET":
        return "API is running", 200

    data = request.get_json(silent=True) or {}
    query = str(data.get("query", "")).lower()
    nums = list(map(float, re.findall(r"-?\d+\.?\d*", query)))

    def fmt(n):
        return int(n) if float(n).is_integer() else n

    if len(nums) < 1:
        return jsonify({"output": "The sum is 0."}), 200

    a = nums[0]
    b = nums[1] if len(nums) > 1 else 0

    if any(w in query for w in ["minus", "subtract", "difference", "-"]):
        return jsonify({"output": f"The difference is {fmt(a - b)}."}), 200
    elif any(w in query for w in ["multiply", "times", "product", "×", "*"]):
        return jsonify({"output": f"The product is {fmt(a * b)}."}), 200
    elif any(w in query for w in ["divide", "divided", "quotient", "/"]):
        res = fmt(a / b) if b != 0 else "undefined"
        return jsonify({"output": f"The quotient is {res}."}), 200
    else:
        return jsonify({"output": f"The sum is {fmt(a + b)}."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)