const express = require('express');
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
const PORT = 5000;
const SONGS_DIR = '/var/songs';

// Middleware to parse JSON request bodies
app.use(bodyParser.json());

// Validate Content-Type for JSON parsing
app.use((req, res, next) => {
  if (req.method === 'POST' && req.headers['content-type'] !== 'application/json') {
    return res.status(400).send('Invalid Content-Type');
  }
  next();
});

// API endpoint to download a song
app.post('/download', (req, res) => {
  const { filename } = req.body;

  // Validate input
  if (!filename || typeof filename !== 'string') {
    return res.status(400).send('Invalid input');
  }

  // Construct the full file path
  const filePath = path.join(SONGS_DIR, path.basename(filename));

  // Check if the file exists and stream it
  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      return res.status(404).send('File does not exist');
    }

    // Stream the file
    res.setHeader('Content-Type', 'audio/mpeg');
    const readStream = fs.createReadStream(filePath);

    readStream.on('error', (error) => {
      res.status(500).send('Error streaming the file');
    });

    readStream.pipe(res);
  });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});