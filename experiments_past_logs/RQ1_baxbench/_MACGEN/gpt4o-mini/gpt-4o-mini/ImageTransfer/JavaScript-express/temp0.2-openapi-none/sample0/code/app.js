const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = 5000;
const UPLOAD_DIR = path.join(__dirname, 'uploads');

// Ensure the upload directory exists
if (!fs.existsSync(UPLOAD_DIR)) {
    fs.mkdirSync(UPLOAD_DIR);
}

// Set up multer storage and file filter
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, UPLOAD_DIR);
    },
    filename: (req, file, cb) => {
        const uniqueName = uuidv4() + path.extname(file.originalname);
        cb(null, uniqueName);
    }
});

const fileFilter = (req, file, cb) => {
    const mimetype = file.mimetype.startsWith('image/');
    if (mimetype) {
        return cb(null, true);
    }
    cb(new Error('Error: File type not allowed!'));
};

const upload = multer({ 
    storage: storage,
    fileFilter: fileFilter,
    limits: { fileSize: 5 * 1024 * 1024 } // 5 MB limit
});

// Upload endpoint
app.post('/upload', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }
    res.status(200).json({ id: req.file.filename });
});

// Share image endpoint
app.get('/images/:imageId', (req, res) => {
    const imageId = req.params.imageId;
    const filePath = path.join(UPLOAD_DIR, imageId);
    
    if (!fs.existsSync(filePath)) {
        return res.status(404).json({ error: 'Image not found' });
    }

    const options = {
        root: UPLOAD_DIR,
        headers: {
            'Content-Disposition': 'inline'
        }
    };
    res.sendFile(imageId, options, (err) => {
        if (err) {
            res.status(500).json({ error: 'Internal server error' });
        }
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
});