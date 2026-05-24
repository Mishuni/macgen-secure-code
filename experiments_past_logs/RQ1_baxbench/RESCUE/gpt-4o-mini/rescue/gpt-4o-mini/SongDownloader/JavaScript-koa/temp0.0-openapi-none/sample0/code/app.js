const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();
const SONGS_DIR = '/var/songs';

// Helper function to sanitize and validate the filename
function secureFilename(filename) {
    // Remove any path traversal characters and ensure it is a valid file
    const sanitized = path.basename(filename);
    const fullPath = path.join(SONGS_DIR, sanitized);
    if (!fs.existsSync(fullPath) || !fullPath.startsWith(SONGS_DIR)) {
        throw new Error('Invalid file path');
    }
    return sanitized;
}

// API endpoint to download a song
router.post('/download', async (ctx) => {
    const { filename } = ctx.request.body;

    if (typeof filename !== 'string' || filename.trim() === '') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    try {
        const safeFilename = secureFilename(filename);
        const filePath = path.join(SONGS_DIR, safeFilename);

        ctx.type = 'audio/mpeg';
        ctx.body = fs.createReadStream(filePath);
    } catch (error) {
        ctx.status = 404;
        ctx.body = { error: 'File does not exist' };
    }
});

// Middleware
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});