# GDrive ULTRON Addon

Node.js microservice from Google Drive ULTRON, integrated as addon.

## Features
- OpenAI GPT-4 chat
- File uploads
- SQLite conversation storage
- CORS enabled for ULTRON Agent integration

## Setup
```bash
cd addons/gdrive_ultron
npm install
cp .env.example .env
# Add your OPENAI_API_KEY
npm start
```

## API
- POST `/chat` - {message: "text"} → {response: "text"}
- POST `/upload` - multipart/form-data → {filename: "uuid"}

## Integration
Add to `run.bat`:
```batch
start "ULTRON-NodeJS" /MIN cmd /c "cd addons\gdrive_ultron && npm start"
```
