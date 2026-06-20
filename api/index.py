from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handle CORS preflight requests
@app.options("/")
async def options_handler():
    return Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Load telemetry data
with open("q-vercel-latency.json", "r") as f:
    telemetry = json.load(f)

class RequestData(BaseModel):
    regions: list[str]
    threshold_ms: int

@app.post("/")
@app.post("")
def analyse(data: RequestData):

    results = {}

    for region in data.regions:

        rows = [
            r for r in telemetry
            if r["region"] == region
        ]

        if not rows:
            continue

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        results[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 2),
            "breaches": sum(
                1 for x in latencies
                if x > data.threshold_ms
            )
        }

    return results