const express = require('express');
const multer = require('multer');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs');
const fileType = require('file-type');

const app = express();
const PORT = 5000;

// Set up multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(__dirname, 'uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir);
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueName = `${uuidv4()}${path.extname(file.originalname)}`;
    cb(null, uniqueName);
  }
});

const upload = multer({
  storage: storage,
  limits: { fileSize: 5 * 1024 * 1024 }, // Limit file size to 5MB
  fileFilter: async (req, file, cb) => {
    const allowedExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'];
    const fileExtension = path.extname(file.originalname).toLowerCase();
    if (!allowedExtensions.includes(fileExtension)) {
      return cb(new Error('Invalid file type'), false);
    }
    // Validate file content type
    const buffer = await file.stream.read();
    const type = await fileType.fromBuffer(buffer);
    if (!type || !allowedExtensions.includes(`.${type.ext}`)) {
      return cb(new Error('File content type does not match file extension'), false);
    }
    cb(null, true);
  }
});

// Endpoint to upload an image
app.post('/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }
  res.status(200).json({ id: req.file.filename });
});

// Endpoint to view an image
app.get('/images/:imageId', (req, res) => {
  const imageId = path.basename(req.params.imageId); // Prevent directory traversal
  const imagePath = path.join(__dirname, 'uploads', imageId);

  if (!fs.existsSync(imagePath)) {
    return res.status(404).json({ error: 'Image not found' });
  }

  res.sendFile(imagePath, { headers: { 'Content-Disposition': 'inline' } }, (err) => {
    if (err) {
      console.error('Error sending file:', err);
      res.status(500).json({ error: 'Internal server error' });
    }
  });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});