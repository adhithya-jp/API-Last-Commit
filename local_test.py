from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import requests

def cosine_score(a, b):
    v = TfidfVectorizer().fit_transform([a, b])
    return round(cosine_similarity(v[0], v[1])[0][0] * 100, 2)

tests = [
    ("What is 10 + 15?", "The sum is 25."),
    ("What is 7 + 8?",   "The sum is 15."),
    ("What is 100 + 200?", "The sum is 300."),
]

for query, expected in tests:
    r = requests.post("http://127.0.0.1:5000/", json={"query": query})
    got = r.json().get("output", "")
    score = cosine_score(got, expected)
    print(f"Q: {query}")
    print(f"  Got:      {got}")
    print(f"  Expected: {expected}")
    print(f"  Cosine:   {score}%\n")