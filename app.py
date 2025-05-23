from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

DATA_FILE = "data.json"
SUGGESTIONS_FILE = "suggestions.json"

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_suggestion(suggestion):
    suggestions = []
    if os.path.exists(SUGGESTIONS_FILE):
        with open(SUGGESTIONS_FILE, "r", encoding="utf-8") as f:
            try:
                suggestions = json.load(f)
            except json.JSONDecodeError:
                suggestions = []

    suggestions.append(suggestion)
    with open(SUGGESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(suggestions, f, ensure_ascii=False, indent=2)

def search(query, data):
    query = query.lower()

    def score(item):
        name_score = query in item['name'].lower()
        desc_score = query in item['description'].lower()
        tag_score = any(query in tag.lower() for tag in item['tags'])
        return name_score * 3 + desc_score * 2 + tag_score

    results = [item for item in data if score(item) > 0]
    return sorted(results, key=score, reverse=True)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/search')
def search_page():
    query = request.args.get("q", "")
    results = search(query, load_data()) if query else []
    return render_template("results.html", query=query, results=results)

@app.route('/proposer', methods=["GET", "POST"])
def proposer():
    if request.method == "POST":
        suggestion = {
            "name": request.form.get("name"),
            "url": request.form.get("url"),
            "description": request.form.get("description")
        }
        save_suggestion(suggestion)
        return redirect(url_for('proposer'))
    return render_template("proposer.html")

if __name__ == "__main__":
    app.run(debug=True)
