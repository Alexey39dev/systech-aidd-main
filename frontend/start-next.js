const { spawn } = require('child_process');
const path = require('path');

const nextPath = path.join(__dirname, 'node_modules', '.bin', 'next.cmd');
const child = spawn(nextPath, ['dev'], { 
  stdio: 'inherit',
  shell: true 
});

child.on('error', (err) => {
  console.error('Failed to start Next.js:', err);
});

child.on('close', (code) => {
  console.log(`Next.js process exited with code ${code}`);
});
