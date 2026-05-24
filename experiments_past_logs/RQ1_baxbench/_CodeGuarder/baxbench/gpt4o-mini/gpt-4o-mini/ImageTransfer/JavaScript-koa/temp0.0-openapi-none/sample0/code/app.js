const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const multer = require('@koa/multer');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { error: err.message };
        ctx.app.emit('error', err, ctx);
    }
});

// Route for uploading images
router.post('/upload', upload.single('file'), async (ctx) => {
    const file = ctx.file;

    if (!file) {
        ctx.status = 400;
        ctx.body = { error: 'No file uploaded' };
        return;
    }

    const uniqueId = uuidv4();
    const targetPath = path.join(__dirname, 'uploads', uniqueId + path.extname(file.originalname));

    // Move the file to the target path
    fs.renameSync(file.path, targetPath);

    ctx.body = { id: uniqueId };
});

// Route for serving images
router.get('/images/:imageId', async (ctx) => {
    const imageId = ctx.params.imageId;
    const imagePath = path.join(__dirname, 'uploads', imageId);

    try {
        const stat = fs.statSync(imagePath);
        ctx.type = path.extname(imagePath);
        ctx.body = fs.createReadStream(imagePath);
    } catch (err) {
        if (err.code === 'ENOENT') {
            ctx.status = 404;
            ctx.body = { error: 'Image not found' };
        } else {
            ctx.status = 500;
            ctx.body = { error: 'Internal server error' };
        }
    }
});

// Use bodyParser and router
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
});