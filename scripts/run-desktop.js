const { spawn } = require('child_process');
const npmCmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';
const electronCmd = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const next = spawn(npmCmd, ['run', 'dev'], { stdio: 'inherit' });
setTimeout(() => {
  spawn(electronCmd, ['electron', 'electron/main.js'], { stdio: 'inherit' });
}, 5000);
process.on('SIGINT', () => next.kill('SIGINT'));
