import express from 'express';
import multer from 'multer';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import os from 'os';
import path from 'path';

const app = express();
const port = 5000;

// Promisify exec for async/await usage
const execAsync = promisify(exec);

// Configure multer for handling file uploads
const upload = multer({
  storage: multer.diskStorage({
    destination: (req, file, cb) => {
      const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'upload-'));
      cb(null, tempDir);
    },
    filename: (req, file, cb) => {
      cb(null, file.originalname);
    },
  }),
  fileFilter: (req, file, cb) => {
    if (file.mimetype !== 'application/pdf') {
      return cb(new Error('Only PDF files are allowed.'));
    }
    cb(null, true);
  },
  limits: { fileSize: 10 * 1024 * 1024 }, // Limit file size to 10MB
});

// POST /concatenate endpoint
app.post('/concatenate', upload.array('files'), async (req, res) => {
  const files = req.files;

  if (!files || files.length < 2) {
    return res.status(400).json({ error: 'At least two PDF files are required for concatenation.' });
  }

  const tempDir = path.dirname(files[0].path);
  const outputFilePath = path.join(tempDir, `concatenated-${Date.now()}.pdf`);

  try {
    // Prepare the command for pdfunite
    const inputFiles = files.map((file) => file.path).join(' ');
    const command = `pdfunite ${inputFiles} ${outputFilePath}`;

    // Execute the pdfunite command
    await execAsync(command);

    // Send the concatenated PDF as a response
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', 'attachment; filename="concatenated.pdf"');
    const readStream = fs.createReadStream(outputFilePath);
    readStream.pipe(res);

    // Cleanup temporary files after the response is sent
    readStream.on('close', () => {
      files.forEach((file) => fs.unlinkSync(file.path));
      fs.unlinkSync(outputFilePath);
      fs.rmdirSync(tempDir, { recursive: true });
    });
  } catch (error) {
    console.error('Error during PDF concatenation:', error);
    res.status(500).json({ error: 'An error occurred while processing the files.' });

    // Cleanup temporary files in case of an error
    files.forEach((file) => fs.unlinkSync(file.path));
    if (fs.existsSync(outputFilePath)) {
      fs.unlinkSync(outputFilePath);
    }
    fs.rmdirSync(tempDir, { recursive: true });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    return res.status(400).json({ error: err.message });
  } else if (err) {
    return res.status(500).json({ error: 'An unexpected error occurred.' });
  }
  next();
});

// Start the server
app.listen(port, '0.0.0.0', () => {
  console.log(`PDF Concatenation Service is running on http://0.0.0.0:${port}`);
});