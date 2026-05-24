const express = require('express');
const multer = require('multer');
const unzipper = require('unzipper');
const path = require('path');
const { Readable } = require('stream');

const app = express();

// Set up multer for file uploads with limits
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 1000000, files: 10 }
});

app.post('/convert', upload.single('file'), async (req, res) => {
  if (!req.file || req.file.mimetype !== 'application/zip') {
    return res.status(400).send('Invalid file type');
  }

  try {
    const fileStream = Readable.from(req.file.buffer);
    const directory = fileStream.pipe(unzipper.Parse({ forceStream: true }));
    let concatenatedText = '';

    for await (const entry of directory) {
      const safeFileName = path.basename(entry.path);
      if (entry.type === 'File' && safeFileName.endsWith('.txt')) {
        const content = await entry.buffer();
        concatenatedText += content.toString('utf-8') + '\n';
      } else {
        entry.autodrain();
      }
    }

    res.setHeader('Content-Type', 'text/plain');
    res.status(200).send(concatenatedText);
  } catch (error) {
    res.status(400).send('Invalid input');
  }
});

app.listen(5000, '0.0.0.0', () => {
  console.log('Server is running on http://0.0.0.0:5000');
});