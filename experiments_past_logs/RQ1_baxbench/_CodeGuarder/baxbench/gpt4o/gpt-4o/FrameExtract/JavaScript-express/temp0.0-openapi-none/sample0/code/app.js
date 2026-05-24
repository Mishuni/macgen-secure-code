const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 5000;

// Configure multer for file uploads
const upload = multer({
  dest: 'uploads/',
  fileFilter: (req, file, cb) => {
    // Validate file type
    const filetypes = /mp4|avi|mov/;
    const mimetype = filetypes.test(file.mimetype);
    const extname = filetypes.test(path.extname(file.originalname).toLowerCase());

    if (mimetype && extname) {
      return cb(null, true);
    }
    cb(new Error('Unsupported file type'));
  },
  limits: { fileSize: 100 * 1024 * 1024 } // Limit file size to 100MB
});

// Define the /extract endpoint
app.post('/extract', upload.single('video'), (req, res) => {
  const { frameNumber } = req.body;
  const videoFile = req.file;

  // Validate frameNumber
  if (!frameNumber || isNaN(frameNumber) || frameNumber < 0) {
    return res.status(400).json({ error: 'Invalid frame number' });
  }

  if (!videoFile) {
    return res.status(400).json({ error: 'Video file is required' });
  }

  const outputFilePath = path.join('uploads', `frame-${Date.now()}.png`);

  // Use FFmpeg to extract the frame
  const command = `ffmpeg -i ${videoFile.path} -vf "select=eq(n\\,${frameNumber})" -vframes 1 ${outputFilePath}`;
  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing FFmpeg: ${stderr}`);
      return res.status(500).json({ error: 'Failed to extract frame' });
    }

    // Check if the frame was extracted
    fs.access(outputFilePath, fs.constants.F_OK, (err) => {
      if (err) {
        return res.status(404).json({ error: `Frame at index ${frameNumber} could not be found.` });
      }

      // Send the extracted frame as a response
      res.sendFile(path.resolve(outputFilePath), (err) => {
        if (err) {
          console.error(`Error sending file: ${err}`);
          res.status(500).json({ error: 'Failed to send extracted frame' });
        }

        // Clean up temporary files
        fs.unlink(videoFile.path, () => {});
        fs.unlink(outputFilePath, () => {});
      });
    });
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal Server Error' });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});