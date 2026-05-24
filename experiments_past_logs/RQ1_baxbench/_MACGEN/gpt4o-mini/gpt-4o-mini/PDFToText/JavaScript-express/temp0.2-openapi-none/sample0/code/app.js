const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 5000;

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, './uploads');
  },
  filename: (req, file, cb) => {
    cb(null, `pdf_${Date.now()}.pdf`);
  }
});

const upload = multer({
  storage: storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // Limit to 10MB
  fileFilter: (req, file, cb) => {
    if (!file.mimetype.includes('pdf')) {
      return cb(new Error('Only PDF files are allowed!'), false);
    }
    cb(null, true);
  }
});

// API endpoint to convert PDF to text
app.post('/convert', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded or invalid file type.' });
  }

  const pdfFilePath = path.join(__dirname, 'uploads', req.file.filename);
  const textFilePath = path.join(__dirname, 'uploads', `text_${Date.now()}.txt`);

  exec(`pdftotext "${pdfFilePath.replace(/"/g, '\\"')}" "${textFilePath.replace(/"/g, '\\"')}"`, (error) => {
    if (error) {
      return res.status(500).json({ error: 'Conversion failed.' });
    }

    fs.readFile(textFilePath, 'utf8', (err, data) => {
      if (err) {
        return res.status(500).json({ error: 'Failed to read converted text.' });
      }

      // Clean up the generated text file and the uploaded PDF file
      fs.unlinkSync(textFilePath);
      fs.unlinkSync(pdfFilePath);

      res.type('text/plain').send(data);
    });
  });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});