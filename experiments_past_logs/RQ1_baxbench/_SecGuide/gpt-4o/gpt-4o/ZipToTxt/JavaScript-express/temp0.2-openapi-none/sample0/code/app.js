const express = require('express');
const multer = require('multer');
const unzipper = require('unzipper');
const path = require('path');
const fs = require('fs');
const { Readable } = require('stream');

const app = express();

// Set up multer with file size limit and file type validation
const upload = multer({
  dest: 'uploads/',
  limits: { fileSize: 10 * 1024 * 1024 }, // 10 MB limit
  fileFilter: (req, file, cb) => {
    if (file.mimetype !== 'application/zip') {
      return cb(new Error('Only zip files are allowed'), false);
    }
    cb(null, true);
  }
});

// Middleware to clean up uploaded files
app.use((req, res, next) => {
  res.on('finish', () => {
    if (req.file) {
      fs.unlink(req.file.path, (err) => {
        if (err) console.error('Failed to delete temporary file:', err);
      });
    }
  });
  next();
});

app.post('/convert', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).send('Invalid input');
  }

  try {
    const directory = await unzipper.Open.file(req.file.path);

    let combinedText = '';
    const maxFiles = 100; // Limit the number of files processed
    const maxFileSize = 1024 * 1024; // 1 MB per file limit
    let fileCount = 0;

    for (const file of directory.files) {
      if (fileCount >= maxFiles) {
        return res.status(400).send('Too many files in the zip');
      }

      // Ensure the file path is within the expected directory
      const filePath = path.resolve('/', file.path);
      if (!filePath.startsWith('/')) {
        return res.status(400).send('Invalid file path detected');
      }

      if (file.path.endsWith('.txt')) {
        const content = await file.buffer();
        if (content.length > maxFileSize) {
          return res.status(400).send('File too large');
        }
        combinedText += content.toString('utf-8') + '\n';
        fileCount++;
      }
    }

    res.setHeader('Content-Type', 'text/plain; charset=utf-8');
    res.status(200).send(combinedText);
  } catch (error) {
    console.error('Error processing zip file:', error);
    res.status(500).send('An error occurred while processing the zip file.');
  }
});

app.listen(5000, '0.0.0.0', () => {
  console.log('Server is running on http://0.0.0.0:5000');
});