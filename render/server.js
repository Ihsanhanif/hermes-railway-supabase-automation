const express = require('express');
const { spawn } = require('child_process');
const app = express();
const PORT = process.env.PORT || 3000;

function ensureHermes() {
  if (globalThis.hermes && !globalThis.hermes.killed) return;
  globalThis.hermes = spawn('hermes', ['--stdio'], { stdio: ['ignore','inherit','inherit'] });
  globalThis.hermes.on('exit', () => { globalThis.hermes = null; setTimeout(ensureHermes, 1000); });
}

app.get('/health', (req, res) => res.sendStatus(200));
app.get('/_ping', (req, res) => { ensureHermes(); res.send('pong'); });

app.listen(PORT, () => {
  ensureHermes();
  console.log('listening on', PORT);
});
