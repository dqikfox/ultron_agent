
import azure.functions as func
import requests

def main(req: func.HttpRequest) -> func.HttpResponse:
    prompt = req.params.get('prompt')
    
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "qwen3-coder:480b-cloud", "prompt": prompt, "stream": False}
    )
    
    return func.HttpResponse(r.json().get("response", ""), status_code=200)
