import express from 'express';
import axios from 'axios';
import readline from 'readline';
import { ElevenLabs } from 'elevenlabs';

const app = express();
const port = 3000;

const elevenlabs = new ElevenLabs({ apiKey: 'sk_a99d3caeef2c2dc6e98567110d905e724af83375e5c29d9d' });
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
      const audio = await elevenlabs.textToSpeech(reply, { voiceId: 'agent_01jz2wq70mfetr2b7nchrhew1t' });
      audio.pipe(fs.createWriteStream('output.mp3'));
      voiceLoop();
    } catch (e) {
      console.error('Ultron failed:', e.message);
      voiceLoop();
    }
  });
}