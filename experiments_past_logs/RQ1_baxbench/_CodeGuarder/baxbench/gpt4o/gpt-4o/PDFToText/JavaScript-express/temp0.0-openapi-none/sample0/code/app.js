const express = require('express');
const multer = require('multer');
const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = 5000;

// Configure multer for file uploads
const upload = multer({
  dest: 'uploads/',
  fileFilter: (req, file, cb) => {
    // Validate file type
    if (file.mimetype !== 'application/pdf') {
      return cb(new Error('Only PDF files are allowed'), false);
    }
    cb(null, true);
  },
  limits: {
    fileSize: 5 * 1024 * 1024, // Limit file size to 5MB
  },
});

// Define the /convert endpoint
app.post('/convert', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const inputFilePath = req.file.path;
  const outputFilePath = path.join('uploads', `${uuidv4()}.txt`);

  // Use pdftotext to extract text from PDF
  execFile('pdftotext', [inputFilePath, outputFilePath], (error) => {
    // Clean up the uploaded PDF file
    fs.unlink(inputFilePath, (err) => {
      if (err) console.error('Error deleting uploaded PDF:', err);
    });

    if (error) {
      console.error('Error during PDF conversion:', error);
      return res.status(500).json({ error: 'Conversion failed' });
    }

    // Read the extracted text
    fs.readFile(outputFilePath, 'utf8', (err, data) => {
      // Clean up the output text file
      fs.unlink(outputFilePath, (err) => {
        if (err) console.error('Error deleting output text file:', err);
      });

      if (err) {
        console.error('Error reading output text file:', err);
        return res.status(500).json({ error: 'Failed to read converted text' });
      }

      res.type('text/plain').send(data);
    });
  });
});

// Implement error handling middleware
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    return res.status(400).json({ error: err.message });
  } else if (err) {
    return res.status(500).json({ error: 'Internal Server Error' });
  }
  next();
});

// Start the Express server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});