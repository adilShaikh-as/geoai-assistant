import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services import get_coordinates, get_weather

app = FastAPI(title="GeoAI Hackathon Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-1.5B-Instruct"
HF_TOKEN = "YOUR_TOKEN_HERE" 

class QueryRequest(BaseModel):
    question: str
    location: str

@app.post("/api/ask")
def ask_assistant(req: QueryRequest):
    coords = get_coordinates(req.location)
    if not coords:
        raise HTTPException(status_code=404, detail="Location not found")
    
    weather = get_weather(coords["lat"], coords["lon"])
    if not weather:
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")
    
    current_weather = weather["current"]
    
    prompt = (
        "System: You are an AI assistant advising on outdoor activities. "
        "Base your recommendation strictly on the provided live weather and location data.\n\n"
        f"User Question: {req.question}\n"
        f"Location: {coords['display_name']}\n"
        f"Live Weather: Temp {current_weather['temperature_2m']}°C, Wind {current_weather['wind_speed_10m']} km/h.\n\n"
        "Assistant:"
    )
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 250, "temperature": 0.3}}
    
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Model inference failed.")
        
    return {
        "query": req.question,
        "grounded_data_used": {"location": coords["display_name"], "weather": current_weather},
        "recommendation": response.json()[0]["generated_text"].strip()
    }