"use client";

import { useState } from "react";
import { MapPin, Wind, Thermometer, Navigation, Loader2 } from "lucide-react";

export default function Home() {
  const [location, setLocation] = useState("");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await fetch("https://fruity-stars-warn.loca.lt", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Bypass-Tunnel-Reminder": "true" 
        },
        body: JSON.stringify({ question, location }),
      });

      if (!res.ok) throw new Error("Failed to fetch recommendation.");
      
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 text-gray-900 p-8 font-sans">
      <div className="max-w-3xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight text-blue-900">GeoAI Outdoors</h1>
          <p className="text-gray-500">Live, data-grounded recommendations for your next activity.</p>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700">Location</label>
              <div className="relative">
                <MapPin className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input 
                  type="text" 
                  required
                  placeholder="e.g., Powai, Mumbai"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-black"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700">Activity & Profile</label>
              <div className="relative">
                <Navigation className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input 
                  type="text" 
                  required
                  placeholder="e.g., Mild asthma, good for a walk?"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-black"
                />
              </div>
            </div>
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors flex justify-center items-center"
          >
            {loading ? <Loader2 className="animate-spin h-5 w-5" /> : "Get Recommendation"}
          </button>
        </form>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-lg border border-red-100 text-center">
            {error}
          </div>
        )}

        {/* Results Card */}
        {result && (
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            <div className="border-b pb-4">
              <h2 className="text-xl font-bold text-gray-800">Grounding Context</h2>
              <p className="text-sm text-gray-500">The live data used to make this decision.</p>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg space-y-1">
                <MapPin className="h-6 w-6 text-blue-600 mb-2" />
                <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Location</p>
                <p className="text-sm font-medium line-clamp-2 text-black">{result.grounded_data_used.location}</p>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg space-y-1">
                <Thermometer className="h-6 w-6 text-orange-600 mb-2" />
                <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Temperature</p>
                <p className="text-xl font-bold text-black">{result.grounded_data_used.weather.temperature_2m}°C</p>
              </div>
              <div className="bg-teal-50 p-4 rounded-lg space-y-1">
                <Wind className="h-6 w-6 text-teal-600 mb-2" />
                <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Wind Speed</p>
                <p className="text-xl font-bold text-black">{result.grounded_data_used.weather.wind_speed_10m} km/h</p>
              </div>
            </div>

            <div className="bg-gray-50 p-6 rounded-lg border border-gray-100">
              <h3 className="text-lg font-bold text-gray-800 mb-3">AI Recommendation</h3>
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                {result.recommendation}
              </p>
            </div>

          </div>
        )}
      </div>
    </main>
  );
}