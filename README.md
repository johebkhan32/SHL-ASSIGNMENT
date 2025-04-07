# SHL-ASSIGNMENT

# 🧠 SHL Assessment Recommender

An intelligent rule-based recommendation system that suggests relevant SHL assessments based on natural language job descriptions, direct URLs, or keyword queries. Built with **Streamlit**, **Python**, and **BeautifulSoup/Selenium** for web scraping.

---

## 🚀 Live Demo

👉 [Click here to try the app](https://johebkhan32-shl-assignment-app-hoe055.streamlit.app/)  
*(No installation needed – runs directly in the browser)*

---

## 🔍 Problem Statement

Hiring managers often struggle to find the right assessments from SHL's product catalog. The current system requires manual filtering, making it time-consuming and inefficient.

### ✅ Solution

This web application allows users to input:
- 🔗 A **direct URL** from SHL's catalog
- 📄 A **job description**
- 📝 A **natural language query**

It returns the **top 1-10 most relevant SHL assessments**, based on:
- Match score from keyword relevance
- Duration compatibility
- Support for **Remote Testing** and **Adaptive/IRT**
- Test types (e.g., Cognitive, Behavioral, Personality)

---

## 🛠 Tech Stack

- **Python 3.9+**
- **Streamlit** – Frontend UI
- **Selenium** – Automated web scraping
- **BeautifulSoup** – HTML parsing
- **JSON / CSV** – Data storage

---

## ⚙️ Getting Started (Local)

### 1. Clone the Repository

```bash
git clone https://github.com/johebkhan32/SHL-ASSIGNMENT.git
cd SHL-ASSIGNMENT
