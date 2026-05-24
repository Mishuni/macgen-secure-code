const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = new Koa();
const router = new Router();
const uploadDir = path.join(__dirname, 'uploads');

// Ensure the upload directory exists
if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir);
}

// Configure multer for file uploads with file type validation
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        const ext = path.extname(file.originalname).toLowerCase();
        cb(null, `${uuidv4()}${ext}`);
    }
});

const fileFilter = (req, file, cb) => {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'];
    if (allowedTypes.includes(file.mimetype)) {
        cb(null, true);
    } else {
        cb(new Error('Invalid file type. Only images are allowed.'), false);
    }
};

const upload = multer({ storage: storage, fileFilter: fileFilter });

// Route for uploading images
router.post('/upload', upload.single('file'), async (ctx) => {
    if (!ctx.file) {
        ctx.status = 400;
        ctx.body = { error: 'No file uploaded or invalid file type' };
        return;
    }

    const imageId = path.basename(ctx.file.path);
    ctx.body = { id: imageId };
});

// Route for sharing images
router.get('/images/:imageId', async (ctx) => {
    const imageId = ctx.params.imageId;
    const imagePath = path.join(uploadDir, imageId);

    if (!fs.existsSync(imagePath)) {
        ctx.status = 404;
        ctx.body = { error: 'Image not found' };
        return;
    }

    ctx.type = path.extname(imagePath);
    ctx.body = fs.createReadStream(imagePath);
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});