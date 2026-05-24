const express = require('express');
const multer = require('multer');
const unzipper = require('unzipper');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = 5000;

// Configure multer for file uploads
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }, // Limit file size to 10MB
});

// Helper function to validate zip entry paths
function isValidZipEntry(entryPath, targetDir) {
  const normalizedPath = path.normalize(path.join(targetDir, entryPath));
  return normalizedPath.startsWith(targetDir);
}

// API endpoint to convert zip file to text
app.post('/convert', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).send('Invalid input: No file uploaded.');
  }

  const tempDir = path.join(__dirname, 'temp', uuidv4());
  fs.mkdirSync(tempDir, { recursive: true });

  try {
    const zip = await unzipper.Open.buffer(req.file.buffer);
    let concatenatedText = '';

    for (const entry of zip.files) {
      if (entry.type === 'File' && entry.path.endsWith('.txt')) {
        if (!isValidZipEntry(entry.path, tempDir)) {
          throw new Error('Invalid zip entry path detected.');
        }

        const content = await entry.buffer();
        concatenatedText += content.toString('utf-8') + '\n';
      }
    }

    res.type('text/plain').send(concatenatedText);
  } catch (error) {
    res.status(400).send('Error processing zip file: ' + error.message);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});