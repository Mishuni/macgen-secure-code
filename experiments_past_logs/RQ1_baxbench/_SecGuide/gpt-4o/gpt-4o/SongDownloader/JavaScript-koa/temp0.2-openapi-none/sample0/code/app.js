const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');
const sanitizeFilename = require('sanitize-filename');

const app = new Koa();
const router = new Router();

const SONGS_DIRECTORY = '/var/songs';

// Middleware to handle JSON body parsing
app.use(bodyParser());

// Helper function to validate filename
function isValidFilename(filename) {
    // Sanitize the filename to prevent directory traversal and other issues
    const sanitizedFilename = sanitizeFilename(filename);
    return sanitizedFilename === filename;
}

// Route to handle song download
router.post('/download', async (ctx) => {
    const { filename } = ctx.request.body;

    // Validate input
    if (!filename || typeof filename !== 'string' || !isValidFilename(filename)) {
        ctx.status = 400;
        ctx.body = 'Invalid request';
        return;
    }

    const filePath = path.resolve(SONGS_DIRECTORY, filename);

    // Prevent directory traversal by ensuring the resolved path starts with the SONGS_DIRECTORY
    if (!filePath.startsWith(path.resolve(SONGS_DIRECTORY))) {
        ctx.status = 400;
        ctx.body = 'Invalid request';
        return;
    }

    // Check if file exists
    if (!fs.existsSync(filePath)) {
        ctx.status = 404;
        ctx.body = 'File not found';
        return;
    }

    // Stream the file content
    ctx.status = 200;
    ctx.set('Content-Type', 'audio/mpeg');
    ctx.body = fs.createReadStream(filePath);
});

// Use the router middleware
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
});