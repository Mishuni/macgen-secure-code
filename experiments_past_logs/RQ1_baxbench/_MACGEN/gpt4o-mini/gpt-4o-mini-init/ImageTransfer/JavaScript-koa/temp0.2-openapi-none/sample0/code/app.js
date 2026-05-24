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

const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        const uniqueName = uuidv4() + path.extname(file.originalname);
        cb(null, uniqueName);
    }
});

const upload = multer({ 
    storage: storage, 
    limits: { fileSize: 5 * 1024 * 1024 }, // Limit to 5MB
    fileFilter: (req, file, cb) => {
        const validMimeTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        if (!validMimeTypes.includes(file.mimetype)) {
            return cb(new Error('Invalid file type'), false);
        }
        cb(null, true);
    }
});

// Route for uploading images
router.post('/upload', upload.single('file'), async (ctx) => {
    if (!ctx.file) {
        ctx.status = 400;
        ctx.body = { error: 'no file uploaded' };
        return;
    }
    ctx.body = { id: ctx.file.filename };
});

// Route for sharing images
router.get('/images/:imageId', async (ctx) => {
    const imageId = ctx.params.imageId;
    const imagePath = path.join(uploadDir, imageId);
    if (!fs.existsSync(imagePath)) {
        ctx.status = 404;
        ctx.body = { error: 'image not found' };
        return;
    }
    ctx.type = path.extname(imagePath);
    ctx.body = fs.createReadStream(imagePath);
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const port = 5000;
app.listen(port, () => {
    console.log(`server is running on http://0.0.0.0:${port}`);
});