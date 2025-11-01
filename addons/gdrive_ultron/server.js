import express from 'express';
import multer from 'multer';
import cors from 'cors';
import sqlite3 from 'sqlite3';
import OpenAI from 'openai';

const app = express();
const PORT = 3001;
const upload = multer({dest: 'data/uploads/'});
const db = new sqlite3.Database('data/conversations.db');
const openai = new OpenAI({apiKey: process.env.OPENAI_API_KEY});

db.run(`CREATE TABLE IF NOT EXISTS conversations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT,
  user_message TEXT,
  ai_response TEXT
)`);

app.use(cors());
app.use(express.json());

app.post('/chat', async (req, res) => {
  const {message} = req.body;
  const completion = await openai.chat.completions.create({
    model: 'gpt-4',
    messages: [{role: 'user', content: message}]
  });
  const response = completion.choices[0].message.content;
  db.run('INSERT INTO conversations VALUES (?, ?, ?, ?)', 
    [null, new Date().toISOString(), message, response]);
  res.json({response});
});

app.post('/upload', upload.single('file'), (req, res) => {
  res.json({filename: req.file.filename});
});

app.listen(PORT, () => console.log(`GDrive addon: http://localhost:${PORT}`));
