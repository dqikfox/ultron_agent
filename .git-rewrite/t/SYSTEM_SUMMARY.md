# Ultron Agent - Environment & Credentials Summary

This document provides a clean, summarized view of the essential information for the Ultron Agent project, extracted from the provided system logs and data dumps.

---

## 1. System Specifications

| Component      | Detail                                  |
| :------------- | :-------------------------------------- |
| **OS**         | Windows 11 Home 64-bit                  |
| **Processor**  | 13th Gen Intel(R) Core(TM) i5-13420H    |
| **Memory**     | 16 GB RAM                               |
| **GPU 1**      | Intel(R) UHD Graphics                   |
| **GPU 2**      | NVIDIA GeForce RTX 3050 Laptop GPU      |
| **Python Path**| `C:/Python310/python.exe`               |

---

## 2. API Keys & Credentials

### AI & LLM Services

| Service         | Key / ID                                                                                                   |
| :-------------- | :--------------------------------------------------------------------------------------------------------- |
| **OpenAI Key**      | `sk-proj-jiSwWCjFJ34lBHUMfUFAMMF_lJiOxcX6-PnoHJrNpB77JPg58sb_7dxspgXbJS5H_wQhv1iXyUT3BlbkFJi-ZkCrgEY0OR9` |
| **OpenAI Org ID**   | `org-KvYmHwMMKbe8lxOMBGvHYvl4`                                                                              |
| **OpenAI Project ID**| `proj_hKLZKFrOynu4SCUm6nspR1PY`                                                                            |
| **Anthropic Key**   | `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` |
| **DeepSeek Key**    | `sk-585fbd0a7885488496c63a123d2b2440`                                                                       |
| **ElevenLabs Key**  | `sk_a99d3caeef2c2dc6e98567110d905e724af83375e5c29d9d`                                                                       |
| **ElevenLabs Agent**| `agent_01jz2wq70mfetr2b7nchrhew1t`                                                                          |
| **Groq API Key**    | `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`                                                                       |
| **Mistral Key**     | `C41ZZpQXmRFy8IwmECDItNZZ9O2RB9sZ`                                                                          |
| **Gemini API Key**  | `AIzaSyAXRBP9DtXP8WzQLVjLs4uP8BSZKNJ5h7A`                                                                       |

### Infrastructure & Database (Supabase)

| Service            | Value                                                                                                 |
| :----------------- | :---------------------------------------------------------------------------------------------------- |
| **Supabase URL**   | `https://jdkddrfloluhkytxdkkh.supabase.co`                                                            |
| **Anon Key**       | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impka2RkcmZsb2x1aGt5dHhka2toIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE1ODYwNjksImV4cCI6MjA2NzE2MjA2OX0.nlMs2YRoC63AnpXTY9KuIFbebF_KjzgWXuxWcPBVX9A` |
| **Service Role Key** | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey...` (Full key available in source)                          |
| **Postgres User**  | `postgres`                                                                                            |
| **Postgres Pass**  | `%RS@havikz1111`                                                                                      |
| **JWT Secret**     | `3QyXN!pa7mDkz&WRj4vtHBNxz2spVzj3pUbe2GnKsQMqLsbFs`                                                     |

### Authentication & Security

| Service               | Value                                                                                                 |
| :-------------------- | :---------------------------------------------------------------------------------------------------- |
| **GitHub Token**      | `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`                                                            |
| **Docker PAT**        | `dckr_pat_ILO7AbAmftrKb2LfIZWt2XX8akk`                                                                |
| **Google Client ID**    | `116464330596-pnppctmgibuvs6bpvnundrl5o0ujonc7.apps.googleusercontent.com`                             |
| **Google Client Secret**| `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`                                                                |
| **reCAPTCHA Site Key**| `0x4AAAAAABk0XHomLT4ggDjr`                                                                           |
| **reCAPTCHA Secret Key**| `0x4AAAAAABk0XHZKJtgOtnHe4Gmi9vpDCJc`                                                                |
| **Vault Encryption Key**| `JvQ8ra7nE5gFwQhLD0xiTkUf23GSwABY`                                                                    |

---

## 3. Python & AI Environment

### Key Python Packages

- `torch`, `torchvision`, `transformers`
- `accelerate`, `vllm`, `safetensors`, `einops`
- `openai`, `anthropic`, `google-generativeai`, `ollama`
- `langchain`, `langsmith`
- `PyQt5`, `tkinter`
- `pynput`, `pyautogui`, `psutil`
- `opencv-python`, `pillow`
- `requests`, `fastapi`, `uvicorn`
- `supabase`, `postgrest`, `web3`
- `qiskit`

### Local Ollama Models

| Name                                                              | Size   | Family/Type       |
| :---------------------------------------------------------------- | :----- | :---------------- |
| `L3.2-8X3B-MOE-Dark-Champion-Inst-18.4B-uncen-ablit_D_AU-Q3_k_s` | 8.3 GB | `llama`           |
| `qwen2.5vl:latest`                                                | 6.0 GB | `qwen` (Vision)   |
| `qwen2.5:latest`                                                  | 4.7 GB | `qwen`            |
| `hermes3:latest`                                                  | 4.7 GB | `hermes`          |
| `phi-3-mini-128k-instruct.Q5_K_M:latest`                          | 2.8 GB | `phi`             |
| `llama3.2:latest`                                                 | 2.0 GB | `llama`           |
| `qikfox/Eleven:latest`                                            | 2.0 GB | `eleven` (TTS)    |
| `Qwen2.5-7B-Mini.Q5_K_S:latest`                                   | 1.9 GB | `qwen`            |
| `mxbai-embed-large:latest`                                        | 669 MB | `mxbai` (Embedding) |
| `qwen3:0.6b`                                                      | 522 MB | `qwen`            |


