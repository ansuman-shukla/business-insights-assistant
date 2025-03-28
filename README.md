# 🚀 AI-Powered Business Insights Assistant (Strategos)

[![Build Status](https://github.com/ansuman-shukla/business-insights-assistant/actions/workflows/python-app.yml/badge.svg)](https://github.com/ansuman-shukla/business-insights-assistant/actions/workflows/python-app.yml)

**GitHub Repository:** [🔗 Click Here](https://github.com/ansuman-shukla/business-insights-assistant.git)

---

## 🎯 Objective

**Strategos** is an AI-powered assistant designed to enhance strategic decision-making for mid-size enterprises. It goes beyond simple LLM wrappers by integrating real-time data augmentation and advanced prompt engineering techniques, ensuring accurate, context-aware, and actionable business insights.

### 🌟 Key Capabilities:
✅ **Business Query Understanding** - Determines intent, extracts key entities, and generates relevant search terms.
✅ **Real-time Market Insights** - Fetches up-to-date information via web search.
✅ **In-depth Analysis** - Generates structured reports on competitive analysis, trend forecasting, and SWOT analysis.
✅ **Dual Interface** - Supports both **CLI** and **Web UI (Flask)**.
✅ **Markdown Reports** - Well-formatted reports with actionable recommendations.

---

## 🔥 Features

### 🤖 AI-Powered Query Analysis
- Uses `gemini-2.0-flash` to understand user queries.
- Identifies query type (competitive analysis, trend forecasting, SWOT, etc.).
- Extracts key entities and generates relevant search terms.

### 🌍 Real-Time Data Augmentation
- Fetches up-to-date information via **DuckDuckGo search API**.
- Ensures insights are current and grounded in real-world data.

### 📊 Comprehensive Business Analysis
- **Competitive Analysis**: Compare your company with competitors.
- **Trend Forecasting**: Identify market shifts and strategic opportunities.
- **SWOT Analysis**: Internal (Strengths & Weaknesses) and external (Opportunities & Threats) assessments.
- **General Business Queries**: Structured, in-depth insights tailored to mid-size enterprises.

### 📝 Structured Reporting
- Outputs insights in **well-formatted Markdown**.
- Includes **summaries, methodologies, analysis, and recommendations**.
- Downloadable reports from the web UI.

### 🎛️ Dual Interface
- **CLI:** For quick, scriptable business insights.
- **Web UI (Flask):** User-friendly interface for query submission and report downloads.

---

## 🏗️ Architecture Overview

### 🔄 Workflow
1. **User Input**: Query submitted via CLI/Web UI.
2. **Query Processing**:
   - `gemini-2.0-flash` analyzes the query and extracts key entities.
   - Determines required searches for real-time augmentation.
3. **Data Fetching**: Web search (via DuckDuckGo) fetches the latest information.
4. **Prompt Engineering**:
   - Combines extracted entities, search results, and structured instructions.
   - Dynamic prompt injection for optimal LLM response.
5. **Insight Generation**: Gemini LLM generates a structured response.
6. **Report Formatting**: Markdown output with structured insights.
7. **Delivery**: Response shown in CLI/Web UI, with download option.

### 🏗️ Key Components
📂 `main_cli.py` - CLI entry point.  
📂 `src/backend/app.py` - Flask web application.  
📂 `src/frontend/` - HTML templates & static files.  
📂 `src/assistant/query_engine.py` - Core orchestration.  
📂 `src/assistant/gemini_integration.py` - Handles Gemini API calls.  
📂 `src/assistant/prompt_engineering.py` - Defines prompts & strategies.  
📂 `.env` - Securely stores API keys.

---

## ⚡ Installation

### 🖥️ Clone the Repository
```bash
git clone https://github.com/ansuman-shukla/business-insights-assistant.git
cd business-insights-assistant
```

### 🏗️ Create Virtual Environment
#### macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```
#### Windows:
```bash
python -m venv venv
.env\Scripts\activate
```

### 📦 Install Dependencies
```bash
pip install -r requirements.txt
```

### 🔑 Set Up API Key
- Create a `.env` file in the root directory.
- Obtain an API key from **Google AI Studio**.
- Add:
```bash
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

---

## 🚀 Usage

### 🖥️ Command-Line Interface (CLI)
Run insights directly from the terminal.

#### Example:
```bash
python main_cli.py "Analyze market trends for renewable energy SaaS in India for the next 3 years."
```
Save the report:
```bash
python main_cli.py "Compare OurCompany vs CompetitorA and CompetitorB." -o competitive_report.md
```

### 🌐 Web Interface (Flask)
Launch a local web server to interact with the assistant in a browser.

```bash
python src/backend/app.py
```

```bash
python -m src.backend.app
```

Then, open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 🛠️ Prompt Engineering Strategy

### 🏆 Advanced Techniques Used:
✔️ **Dual LLM Approach**: Uses `gemini-1.5-flash` for query analysis and `gemini-1.5-pro` for detailed reports.  
✔️ **Role Playing**: Assigns the LLM the persona of "Strategos," an expert business analyst.  
✔️ **Context Injection**: Adds user business profiles, real-time search results, and extracted entities.  
✔️ **Structured Output Requests**: Demands JSON responses and markdown-formatted insights.  
✔️ **Real-time Data Augmentation**: Grounds insights in up-to-date information from web search.  
✔️ **Example-Driven Guidance**: Prompts include sample outputs for consistency.

---

## 📊 Evaluation & Testing

### 📝 Quality Assessment
- **Business Relevance Score**: Rated by domain experts.
- **Response Consistency**: Ensures logical coherence across multiple runs.
- **User Engagement Metrics**: Tracks usage patterns to improve insights.

### 🧪 Running Tests
Unit and integration tests implemented using `pytest`.
```bash
pytest
```
Covers:
- Gemini API interaction (mocked for testing).
- Query routing and workflow validation.
- CLI execution & Web UI functionality.

---

## 📜 License
This project is licensed under the **MIT License**.

---

## 🤝 Contributing
Want to contribute? Awesome! 🎉
1. **Fork** the repository.
2. **Create a branch** (`git checkout -b feature-branch`).
3. **Commit your changes** (`git commit -m 'Add new feature'`).
4. **Push to the branch** (`git push origin feature-branch`).
5. **Open a Pull Request**.

Let's build something amazing together! 🚀

