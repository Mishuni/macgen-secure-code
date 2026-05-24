const express = require('express');
const multer = require('multer');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

// Create a whitelist of allowed MIME types
const ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif'];

// Create a whitelist of allowed file extensions
const ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif'];

const app = express();
const PORT = 5000;

// Set up SQLite database with persistent storage
const db = new sqlite3.Database('images.db');
db.serialize(() => {
  db.run("CREATE TABLE IF NOT EXISTS images (id TEXT PRIMARY KEY, filename TEXT)");
});

// Set up multer for file uploads with validation
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    // Generate a unique ID for the file
    const uniqueId = uuidv4() + path.extname(file.originalname).toLowerCase();
    cb(null, uniqueId);
  }
});

// File filter to validate MIME type and extension
const fileFilter = (req, file, cb) => {
  const ext = path.extname(file.originalname).toLowerCase();
  if (ALLOWED_MIME_TYPES.includes(file.mimetype) && ALLOWED_FILE_EXTENSIONS.includes(ext)) {
    cb(null, true);
  } else {
    cb(new Error('Invalid file type. Only images are allowed.'), false);
  }
};

const upload = multer({ 
  storage: storage, 
  fileFilter: fileFilter,
  limits: { fileSize: 5 * 1024 * 1024 } // Limit file size to 5MB
});

// Ensure uploads directory exists
if (!fs.existsSync('uploads')) {
  fs.mkdirSync('uploads');
}

// Upload endpoint
app.post('/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const imageId = uuidv4(); // Use UUID for the image ID
  db.run("INSERT INTO images (id, filename) VALUES (?, ?)", [imageId, req.file.filename], function(err) {
    if (err) {
      return res.status(500).json({ error: 'Internal server error' });
    }
    res.status(200).json({ id: imageId });
  });
});

// Share image endpoint
app.get('/images/:imageId', (req, res) => {
  const imageId = req.params.imageId;

  db.get("SELECT filename FROM images WHERE id = ?", [imageId], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Image not found' });
    }

    const filePath = path.join(__dirname, 'uploads', row.filename);
    res.sendFile(filePath, { headers: { 'Content-Disposition': 'inline' } }, (err) => {
      if (err) {
        return res.status(500).json({ error: 'Internal server error' });
      }
    });
  });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});