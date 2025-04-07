import json
import re
from fastapi import FastAPI, Query
from typing import List, Dict, Any

# ------------------------ Load Data ------------------------

def load_data() -> List[Dict[str, Any]]:
    try:
        with open("individual_test_solutions.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Warning: Data file not found. Returning empty list.")
        return []

# Load data once at startup
data = load_data()

# ------------------------ Duration Extractor ------------------------

def extract_minutes(text: str) -> int | None:
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else None

# ------------------------ Recommendation Logic ------------------------

def recommend(query: str, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    query = query.strip().lower().rstrip('/')
    query_tokens = re.findall(r'\w+', query)

    # 1️⃣ Direct URL match
    for item in data:
        item_url = item.get("link", "").strip().lower().rstrip('/')
        if item_url == query:
            item["duration"] = extract_minutes(item.get("assessment_length", ""))
            return [item]

    duration_match = re.search(r'(\d+)\s*(minutes|min)', query)
    max_duration = int(duration_match.group(1)) if duration_match else None

    results = []

    for item in data:
        score = 0
        matched_keywords = []

        title = item.get("title", "").lower()
        description = item.get("description", "").lower()
        combined_text = title + " " + description

        for token in query_tokens:
            if token in combined_text:
                score += 1
                matched_keywords.append(token)

        raw_duration = item.get("assessment_length", "")
        duration = extract_minutes(raw_duration)
        item["duration"] = duration

        if max_duration is not None and duration is not None:
            if duration > max_duration:
                continue
            else:
                score += 1

        if score > 0:
            item["match_score"] = score
            item["matched_keywords"] = matched_keywords
            results.append(item)

    sorted_results = sorted(results, key=lambda x: x.get("match_score", 0), reverse=True)
    return sorted_results[:10]

# ------------------------ FastAPI Endpoint ------------------------

app = FastAPI(
    title="SHL Assessment Recommender API",
    description="API for recommending SHL assessments based on job descriptions or queries",
    version="1.0.0"
)

@app.get("/recommend")
async def get_recommendations(query: str = Query(..., description="Job description or query text")):
    matches = recommend(query, data)
    return {"results": matches}

@app.get("/")
async def root():
    return {"message": "Welcome to SHL Assessment Recommender API. Use /recommend?query=your-query to get recommendations."} 