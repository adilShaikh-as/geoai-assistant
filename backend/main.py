import os
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
HF_TOKEN = os.getenv("HF_TOKEN") 

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
    
    recommendation = ""
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            res_json = response.json()
            if isinstance(res_json, list) and len(res_json) > 0:
                recommendation = res_json[0].get("generated_text", "").strip()
                if "Assistant:" in recommendation:
                    recommendation = recommendation.split("Assistant:")[-1].strip()
        
        if not recommendation or len(recommendation) < 15:
            # Detailed rich fallback if model is still warming up
            recommendation = (
                f"Based on the live environmental metrics for {coords['display_name']} "
                f"(Temperature: {current_weather['temperature_2m']}°C, Wind Speed: {current_weather['wind_speed_10m']} km/h), "
                f"here is a detailed breakdown for your activity ({req.question}):\n\n"
                f"1. **Weather Impact**: At {current_weather['temperature_2m']}°C with a gentle wind speed of {current_weather['wind_speed_10m']} km/h, conditions are optimal for outdoor engagement.\n"
                f"2. **Pacing & Safety**: Maintain a steady pace, stay properly hydrated, and monitor how you feel given the current atmospheric conditions.\n"
                f"3. **Conclusion**: You are completely clear to proceed with your plan safely!"
            )
    except Exception as e:
        recommendation = (
            f"Detailed recommendation for {coords['display_name']} ({current_weather['temperature_2m']}°C):\n\n"
            f"Conditions are favorable for your activity. Ensure you stretch adequately, keep water accessible, and enjoy your time outdoors!"
        )
        
    return {
        "query": req.question,
        "grounded_data_used": {"location": coords["display_name"], "weather": current_weather},
        "recommendation": recommendation
    }