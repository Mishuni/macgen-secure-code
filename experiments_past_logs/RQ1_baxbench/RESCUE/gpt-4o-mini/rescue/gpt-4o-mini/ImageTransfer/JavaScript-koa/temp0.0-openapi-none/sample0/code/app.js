const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const path = require('path');
const fs = require('fs');

const app = new Koa();
const router = new Router();
const uploadDir = path.join(__dirname, 'uploads');

// Ensure the upload directory exists
if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir);
}

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        const ext = path.extname(file.originalname);
        const filename = `${Date.now()}${ext}`;
        cb(null, filename);
    }
});

const upload = multer({ storage: storage });

// Route for uploading images
router.post('/upload', upload.single('file'), async (ctx) => {
    if (!ctx.file) {
        ctx.status = 400;
        ctx.body = { error: 'No file uploaded' };
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

    ctx.type = path.extname(imagePath); // Set the correct mime type
    ctx.body = fs.createReadStream(imagePath);
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});