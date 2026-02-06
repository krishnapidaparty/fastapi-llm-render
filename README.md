# fastapi-llm-render

A FastAPI application with health check, text summarization, and sentiment analysis endpoints powered by OpenAI.

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install fastapi uvicorn python-dotenv openai
   ```

2. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. Run the app:
   ```bash
   uvicorn main:app --reload
   ```

4. Open the API docs at http://127.0.0.1:8000/docs

## Endpoints

- **GET /health** — Health check (status + timestamp)
- **POST /summarize** — Summarize text with a max word length (body: `text`, `max_length`)
- **POST /analyze-sentiment** — Analyze sentiment (body: `text`); returns sentiment, confidence_score, explanation

---

## Summarization Prompt Experimentation

| Variation | Description | Finding |
|-----------|-------------|---------|
| **1** | "Summarize the following text in at most N words: ..." | Works well but can be too literal and sometimes ignores the length constraint. |
| **2** | "Provide a concise summary of the following text, not exceeding N words: ..." | Better; more direct and consistently adheres to the length constraint. |
| **3** | "You are an expert summarizer. Distill the key points ... into a summary of no more than N words: ..." | **(Best)** The role-playing prompt consistently produces the most coherent and insightful summaries, likely because it sets a clearer context and persona for the LLM. |

**Recommendation:** Use Variation 3 (expert summarizer) for production.

---

## Sentiment Analysis Prompt Experimentation

| Variation | Description | Finding |
|-----------|-------------|---------|
| **1** | Full instructions: "Analyze the sentiment ... return sentiment (positive/negative/neutral), confidence score 0–1, and brief explanation. Format as JSON with keys ..." | Most reliable JSON output; explicit format reduces parsing errors. |
| **2** | Simpler: "What is the sentiment of this text? Respond with JSON containing 'sentiment', 'confidence_score', and 'explanation'." | Shorter and often sufficient; occasionally less consistent structure. |
| **3** | Chain of thought: "First, think about the sentiment ... Then, provide a JSON object with ..." | Can improve reasoning but may add extra text before/after the JSON, requiring more robust parsing. |

**Recommendation:** Use Variation 1 when you need consistent JSON; use Variation 2 for simpler prompts if your parser handles minor variations.
