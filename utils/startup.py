import logging
import requests
import subprocess
import time
from config import Config

def ensure_ollama_running(config: Config) -> None:
    """Check if Ollama is running and the model is loaded. If not, start it."""
    model_name = config.get("llm_model", "qwen2.5")
    base_url = config.get("ollama_base_url", "http://localhost:11434")
    
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=3)
        response.raise_for_status()
        
        models = response.json().get("models", [])
        if any(model_name in m.get("name", "") for m in models):
            logging.info(f"Ollama is running and model '{model_name}' is available. - startup.py:18")
            return
        else:
            logging.warning(f"Ollama is running but model '{model_name}' is not loaded. Attempting to load... - startup.py:21")
            _load_ollama_model(model_name)
            return
            
    except (requests.RequestException, requests.exceptions.HTTPError) as e:
        logging.warning(f"Ollama not responding: {e}. Attempting to start service... - startup.py:26")
        _start_ollama_service(model_name)
    except Exception as e:
        logging.error(f"An unexpected error occurred while checking Ollama: {e} - startup.py:29")
        # Decide if we should proceed or exit

def _load_ollama_model(model_name: str) -> None:
    """Internal function to load an Ollama model."""
    try:
        # This command will pull the model if not present and load it.
        subprocess.run(["ollama", "run", model_name], check=True, capture_output=True, text=True)
        logging.info(f"Successfully loaded Ollama model '{model_name}'. - startup.py:37")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logging.error(f"Failed to load Ollama model '{model_name}': {e} - startup.py:39")

def _start_ollama_service(model_name: str) -> None:
    """Internal function to start the Ollama service."""
    try:
        # Use Popen for non-blocking start
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logging.info("Ollama service started. Waiting for it to become available... - startup.py:46")
        time.sleep(5)  # Initial wait
        
        # Verify service is up
        base_url = "http://localhost:11434"
        for i in range(10): # 10 attempts, 2s sleep = 20s total
            try:
                response = requests.get(f"{base_url}/api/tags", timeout=2)
                if response.status_code == 200:
                    logging.info("Ollama service is now running. - startup.py:55")
                    _load_ollama_model(model_name)
                    return
            except requests.RequestException:
                pass
            time.sleep(2)
        
        logging.error("Ollama service did not become available in time. - startup.py:62")
        
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logging.error(f"Failed to start Ollama service: {e} - startup.py:65")

