const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

const SONGS_DIR = '/var/songs';

router.post('/download', async (ctx) => {
    const { filename } = ctx.request.body;

    // Input Validation
    if (!filename || typeof filename !== 'string' || !/^[a-zA-Z0-9_\-\.]+\.mp3$/.test(filename)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    // Path Sanitization
    const safeFilename = path.basename(filename);
    const filePath = path.join(SONGS_DIR, safeFilename);

    // File Existence Check
    if (!filePath.startsWith(SONGS_DIR)) {
        ctx.status = 404;
        ctx.body = { error: 'File does not exist' };
        return;
    }

    try {
        await fs.promises.access(filePath); // Check if file exists
        ctx.set('Content-Type', 'audio/mpeg');
        ctx.body = fs.createReadStream(filePath); // Stream the file
    } catch (err) {
        ctx.status = 404;
        ctx.body = { error: 'File does not exist' };
    }
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});