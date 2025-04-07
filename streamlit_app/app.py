import streamlit as st
import json
import re
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

# ------------------------ Streamlit UI ------------------------

def main():
    st.set_page_config(page_title="SHL Assessment Recommender", layout="wide")
    st.title("🔍 SHL Assessment Recommender")
    st.markdown("Paste a job description, natural language query, or SHL test URL to get relevant recommendations.")

    query = st.text_area("Enter Job Description / Query / SHL Test URL", height=150)

    if st.button("Get Recommendations") and query.strip():
        with st.spinner("Analyzing query..."):
            matches = recommend(query, data)

        if matches:
            st.subheader("Top Matching Assessments")
            results = []
            for match in matches:
                results.append({
                    "Title": match.get("title"),
                    "Link": match.get("link"),
                    "Duration (min)": match.get("duration", "N/A"),
                    "Remote": "Yes" if match.get("remote_testing") else "No",
                    "Adaptive": "Yes" if match.get("adaptive_irt") else "No",
                    "Test Types": ", ".join(match.get("test_types", [])),
                })
            st.dataframe(results)
        else:
            st.warning("No matching assessments found.")

if __name__ == "__main__":
    main()



