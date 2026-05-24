const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

// Middleware to parse JSON request bodies
app.use(bodyParser());

// POST route for downloading songs
router.post('/download', async (ctx) => {
    const { filename } = ctx.request.body;

    // Validate the filename
    if (typeof filename !== 'string' || filename.trim() === '') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    // Sanitize the filename to prevent directory traversal
    const sanitizedFilename = path.basename(filename);
    const filePath = path.join('/var/songs', sanitizedFilename);

    // Check if the file exists
    if (!fs.existsSync(filePath)) {
        ctx.status = 404;
        ctx.body = { error: 'File does not exist' };
        return;
    }

    // Set response headers for audio file
    ctx.set('Content-Type', 'audio/mpeg');
    ctx.set('Content-Disposition', `attachment; filename="${sanitizedFilename}"`);

    // Stream the file to the response
    const readStream = fs.createReadStream(filePath);
    ctx.body = readStream;

    // Handle errors during streaming
    readStream.on('error', (err) => {
        ctx.status = 400;
        ctx.body = { error: 'Error reading file' };
    });
});

// Attach the router to the Koa application
app.use(router.routes()).use(router.allowedMethods());

// Start the Koa server on port 5000
app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});