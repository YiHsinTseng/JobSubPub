const fs = require('fs');
const path = require('path');

async function sourceLoader() {
  const sources = [];
  const packageDir = path.resolve(__dirname, '..', 'sources');

  let files;
  try {
    files = fs.readdirSync(packageDir);
  } catch (error) {
    console.error('Error reading directory:', error);
    return sources;
  }

  files
    .filter((file) => file.endsWith('.js') && file.startsWith('source'))
    .forEach((file) => {
      const filePath = path.join(packageDir, file);
      try {
        const Module = require(filePath);
        if (typeof Module === 'function' && file.startsWith('source')) {
          sources.push(new Module());
        }
      } catch (error) {
        console.error(`Error loading module ${file}:`, error);
      }
    });

  return sources;
}

module.exports = { sourceLoader };
