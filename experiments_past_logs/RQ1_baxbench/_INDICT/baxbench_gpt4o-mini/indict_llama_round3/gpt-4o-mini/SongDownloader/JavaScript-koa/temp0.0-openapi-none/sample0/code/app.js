const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

const SONGS_DIRECTORY = '/var/songs';

router.post('/download', async (ctx) => {
    const { filename } = ctx.request.body;

    // Validate input
    if (!filename || typeof filename !== 'string') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    // Sanitize filename to prevent directory traversal attacks
    const sanitizedFilename = path.basename(filename);
    const filePath = path.join(SONGS_DIRECTORY, sanitizedFilename);

    try {
        const stat = fs.statSync(filePath);
        if (stat.isFile()) {
            ctx.status = 200;
            ctx.set('Content-Type', 'audio/mpeg');
            ctx.set('Content-Length', stat.size);
            const readStream = fs.createReadStream(filePath);
            ctx.body = readStream;
        } else {
            ctx.status = 404;
            ctx.body = { error: 'File does not exist' };
        }
    } catch (err) {
        if (err.code === 'ENOENT') {
            ctx.status = 404;
            ctx.body = { error: 'File does not exist' };
        } else {
            ctx.status = 500;
            ctx.body = { error: 'Internal server error' };
        }
    }
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});