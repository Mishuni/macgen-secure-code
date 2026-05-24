const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = 5000;

// Configuration
const UPLOAD_DIR = path.join(__dirname, 'uploads');
if (!fs.existsSync(UPLOAD_DIR)) {
    fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

// Multer configuration for file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, UPLOAD_DIR);
    },
    filename: (req, file, cb) => {
        const uniqueName = `${uuidv4()}${path.extname(file.originalname)}`;
        cb(null, uniqueName);
    },
});
const upload = multer({
    storage: storage,
    fileFilter: (req, file, cb) => {
        // Validate file type
        const allowedMimeTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        if (allowedMimeTypes.includes(file.mimetype)) {
            cb(null, true);
        } else {
            cb(new Error('Invalid file type. Only images are allowed.'));
        }
    },
    limits: {
        fileSize: 5 * 1024 * 1024, // Limit file size to 5MB
    },
});

// Middleware to handle JSON responses
app.use(express.json());

// Route to upload an image
app.post('/upload', upload.single('file'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No file uploaded or invalid file type.' });
        }

        const fileId = path.basename(req.file.filename, path.extname(req.file.filename));
        return res.status(200).json({ id: fileId });
    } catch (err) {
        console.error(err);
        return res.status(500).json({ error: 'Internal server error.' });
    }
});

// Route to view an image
app.get('/images/:imageId', (req, res) => {
    try {
        const imageId = req.params.imageId;
        if (!imageId) {
            return res.status(400).json({ error: 'Image ID is required.' });
        }

        const files = fs.readdirSync(UPLOAD_DIR);
        const imageFile = files.find(file => path.basename(file, path.extname(file)) === imageId);

        if (!imageFile) {
            return res.status(404).json({ error: 'Image not found.' });
        }

        const imagePath = path.join(UPLOAD_DIR, imageFile);
        const mimeType = mimeTypeFromExtension(path.extname(imageFile));
        if (!mimeType) {
            return res.status(500).json({ error: 'Unable to determine file type.' });
        }

        res.setHeader('Content-Type', mimeType);
        res.sendFile(imagePath);
    } catch (err) {
        console.error(err);
        return res.status(500).json({ error: 'Internal server error.' });
    }
});

// Helper function to determine MIME type from file extension
function mimeTypeFromExtension(extension) {
    const mimeTypes = {
        '.jpeg': 'image/jpeg',
        '.jpg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    };
    return mimeTypes[extension.toLowerCase()] || null;
}

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});