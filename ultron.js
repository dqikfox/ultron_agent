import axios from 'axios';
import { ElevenLabs } from 'elevenlabs';
import express from 'express';
import fs from 'fs';
import readline from 'readline';

const app = express();
const port = 3000;

const elevenlabs = new ElevenLabs({ apiKey: 'a831a3df8229fdbf27173e8157e558200528564937c55a093e10ff752bf98bed' });
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

app.use(express.static('public'));
app.get('/', (req, res) => {
  res.sendFile('index.html', { root: 'public' });
});

app.listen(port, () => {
  console.log(`Ultron online at http://localhost:${port}`);
  voiceLoop();
});

async function voiceLoop() {
  rl.question('Speak to Ultron: ', async (input) => {
    try {
      const response = await axios.post('http://localhost:11434/api/chat', {
        model: 'llama3.2:latest',
        messages: [{ role: 'user', content: input }],
        temperature: 0.5,
        max_tokens: 512
      });
      const reply = response.data.message.content.trim();
      console.log(`Ultron: ${reply}`);
      const audio = await elevenlabs.textToSpeech(reply, { voiceId: 'agent_01jzwkf7dkfdvt5810x1vgrcjs' });
      audio.pipe(fs.createWriteStream('output.mp3'));
      voiceLoop();
    } catch (e) {
      console.error('Ultron failed:', e.message);
      voiceLoop();
    }
  });
}
