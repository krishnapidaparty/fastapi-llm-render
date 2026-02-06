import json
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from openai import OpenAI

from config import OPENAI_API_KEY

app = FastAPI()
client = OpenAI(api_key=OPENAI_API_KEY)


class SummarizeRequest(BaseModel):
    text: str
    max_length: int


class AnalyzeSentimentRequest(BaseModel):
    text: str


@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now()}


@app.post("/summarize")
async def summarize(request: SummarizeRequest):
    try:
        # --- Prompt Variation 1 ---
        #prompt = f"Summarize the following text in at most {request.max_length} words: {request.text}"
        # --- Prompt Variation 2 (More direct) ---
        #prompt = f"Provide a concise summary of the following text, not exceeding {request.max_length} words:\n\n{request.text}"
        # --- Prompt Variation 3 (Role-playing) ---
        prompt = f"You are an expert summarizer. Distill the key points of the following text into a summary of no more than {request.max_length} words:\n\n{request.text}"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=request.max_length * 2,
        )
        summary = response.choices[0].message.content.strip()
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-sentiment")
async def analyze_sentiment(request: AnalyzeSentimentRequest):
    try:
        # --- Prompt Variation 1 ---
        # prompt = f"Analyze the sentiment of the following text and return the sentiment (positive, negative, or neutral), a confidence score from 0 to 1, and a brief explanation. Format the output as a JSON object with keys 'sentiment', 'confidence_score', and 'explanation'.\n\nText: {request.text}"
        # --- Prompt Variation 2 (Simpler) ---
        # prompt = f"What is the sentiment of this text? Respond with JSON containing 'sentiment', 'confidence_score', and 'explanation'.\n\n{request.text}"
        # --- Prompt Variation 3 (Chain of Thought) ---
        prompt = f"First, think about the sentiment of the following text. Then, provide a JSON object with 'sentiment', 'confidence_score', and 'explanation'.\n\nText: {request.text}"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )
        raw = response.choices[0].message.content.strip()

        # Extract JSON from response (handles markdown code blocks or extra text)
        raw_clean = re.sub(r"^```(?:json)?\s*", "", raw).strip()
        try:
            result = json.loads(raw_clean)
            return result
        except json.JSONDecodeError:
            pass
        start = raw.find("{")
        if start != -1:
            depth, end = 0, start
            for i, c in enumerate(raw[start:], start):
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
            if depth == 0:
                result = json.loads(raw[start : end + 1])
                return result
        raise ValueError(f"Could not parse JSON from response: {raw}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON from model: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
