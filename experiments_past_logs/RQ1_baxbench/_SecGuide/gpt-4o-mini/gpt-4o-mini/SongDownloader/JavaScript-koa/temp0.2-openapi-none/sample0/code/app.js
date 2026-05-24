const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs').promises; // Use promises for non-blocking file system operations
const path = require('path');
const mime = require('mime-types'); // Library to determine MIME type
const koaCors = require('@koa/cors'); // CORS middleware

const app = new Koa();
const router = new Router();

// Middleware to handle JSON body parsing
app.use(bodyParser({
    jsonLimit: '1mb' // Limit the size of the request body
}));

// CORS configuration
app.use(koaCors({
    origin: '*', // Adjust this to specify allowed origins
}));

// Define the download route
router.post('/download', async (ctx) => {
    const { filename } = ctx.request.body;

    // Validate the filename input
    if (typeof filename !== 'string' || filename.trim() === '') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    // Sanitize the filename to prevent directory traversal attacks
    const sanitizedFilename = path.basename(filename);
    const filePath = path.join('/var/songs', sanitizedFilename);

    try {
        // Check if the file exists and is readable
        await fs.access(filePath);

        // Dynamically set the Content-Type based on the file extension
        const contentType = mime.lookup(sanitizedFilename) || 'application/octet-stream';
        ctx.set('Content-Type', contentType);
        ctx.set('Content-Disposition', `attachment; filename="${encodeURIComponent(sanitizedFilename)}"`);

        // Stream the file to the response
        const readStream = fs.createReadStream(filePath);
        ctx.body = readStream;

    } catch (error) {
        // Handle file not found or permission denied errors
        if (error.code === 'ENOENT') {
            ctx.status = 404;
            ctx.body = { error: 'File does not exist' };
        } else if (error.code === 'EACCES') {
            ctx.status = 403;
            ctx.body = { error: 'Permission denied' };
        } else {
            ctx.status = 500;
            ctx.body = { error: 'Internal server error' };
            console.error('Error accessing file:', error); // Log the error for debugging
        }
    }
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});