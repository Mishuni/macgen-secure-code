const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const path = require('path');
const fs = require('fs').promises; // Use promises for async file operations
const { v4: uuidv4 } = require('uuid');
const fileType = require('file-type'); // Library to check file type

const app = new Koa();
const router = new Router();
const uploadDir = path.join(__dirname, 'uploads');

// Ensure the upload directory exists
fs.mkdir(uploadDir, { recursive: true }).catch(err => console.error('Failed to create upload directory:', err));

// Configure multer for file uploads with file type validation and size limit
const allowedTypes = /jpeg|jpg|png|gif/; // Example allowed types
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        const uniqueName = `${uuidv4()}${path.extname(file.originalname)}`;
        cb(null, uniqueName);
    }
});

const upload = multer({
    storage: storage,
    limits: { fileSize: 5 * 1024 * 1024 }, // Limit to 5MB
    fileFilter: async (req, file, cb) => {
        const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
        const mimetype = allowedTypes.test(file.mimetype);
        
        // Check the actual file type
        const buffer = file.buffer;
        const type = await fileType.fromBuffer(buffer);
        
        if (extname && mimetype && type && allowedTypes.test(type.ext)) {
            return cb(null, true);
        }
        cb(new Error('Error: File type not allowed!'));
    }
});

// Route for uploading images
router.post('/upload', upload.single('file'), async (ctx) => {
    if (!ctx.file) {
        ctx.status = 400;
        ctx.body = { error: 'No file uploaded' };
        return;
    }

    const imageId = path.basename(ctx.file.filename, path.extname(ctx.file.filename));
    ctx.body = { id: imageId };
});

// Route for sharing images
router.get('/images/:imageId', async (ctx) => {
    const imageId = ctx.params.imageId;
    const safePath = path.join(uploadDir, `${imageId}.*`); // Prevent directory traversal
    const files = await fs.readdir(uploadDir);
    const file = files.find(file => file.startsWith(imageId));

    if (!file) {
        ctx.status = 404;
        ctx.body = { error: 'Image not found' };
        return;
    }

    ctx.type = path.extname(file);
    ctx.body = fs.createReadStream(path.join(uploadDir, file));
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Set security headers
app.use(async (ctx, next) => {
    ctx.set('X-Content-Type-Options', 'nosniff');
    ctx.set('X-Frame-Options', 'DENY');
    ctx.set('Content-Security-Policy', "default-src 'self'");
    ctx.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains'); // HSTS
    ctx.set('X-XSS-Protection', '1; mode=block'); // XSS Protection
    await next();
});

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});