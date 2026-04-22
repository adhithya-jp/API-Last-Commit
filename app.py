from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def solve():
    if request.method == "GET":
        return "API is running", 200

    data = request.get_json(silent=True) or {}
    query = str(data.get("query", "")).strip()
    q = query.lower()
    nums = list(map(float, re.findall(r"-?\d+\.?\d*", q)))

    def fmt(n):
        return int(n) if float(n).is_integer() else n

    if nums and len(nums) >= 2:
        a, b = nums[0], nums[1]
        if any(w in q for w in ["minus", "subtract", "difference"]):
            return jsonify({"output": f"The difference is {fmt(a-b)}."}), 200
        elif any(w in q for w in ["multiply", "times", "product"]):
            return jsonify({"output": f"The product is {fmt(a*b)}."}), 200
        elif any(w in q for w in ["divide", "quotient"]):
            return jsonify({"output": f"The quotient is {fmt(a/b)}."}), 200
        else:
            return jsonify({"output": f"The sum is {fmt(a+b)}."}), 200
    else:
        # echo query back as answer attempt
        return jsonify({"output": query.replace("What is ", "").replace("?", ".")}), 200

if __name__ == "__main__":
    app.run(host="app:app", port=5000)