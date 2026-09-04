"""API bridge between Ultron Agent and NAT"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import asyncio

app = FastAPI(title="Ultron-NAT Bridge")

class ChatRequest(BaseModel):
    message: str
    workflow: str = "workflow.yml"

class UltronNATBridge:
    def __init__(self):
        self.nat_base_url = "http://localhost:5000"  # NAT API server
        
    async def send_to_nat(self, message: str, workflow: str):
        """Send message to NAT and get response"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.nat_base_url}/chat",
                    json={"message": message, "workflow": workflow}
                )
                return response.json()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

bridge = UltronNATBridge()

@app.post("/ultron/chat")
async def ultron_chat(request: ChatRequest):
    """Ultron Agent chat endpoint using NAT backend"""
    result = await bridge.send_to_nat(request.message, request.workflow)
    return {"response": result, "source": "NAT"}

@app.get("/health")
async def health():
    return {"status": "healthy", "bridge": "ultron-nat"}