const Koa = require('koa');
const Router = require('koa-router');
const koaBody = require('@koa/multer')();
const unzipper = require('unzipper');
const fs = require('fs');
const stream = require('stream');

const app = new Koa();
const router = new Router();

router.post('/convert', koaBody.single('file'), async (ctx) => {
    const zipFile = ctx.file;

    if (!zipFile) {
        ctx.status = 400;
        ctx.body = 'Invalid input';
        return;
    }

    const textContents = [];

    try {
        const zipStream = fs.createReadStream(zipFile.path)
            .pipe(unzipper.Parse());

        for await (const entry of zipStream) {
            if (entry.type === 'File' && entry.path.endsWith('.txt')) {
                const content = await streamToString(entry);
                textContents.push(content);
            }
            entry.autodrain();
        }

        ctx.status = 200;
        ctx.body = textContents.join('\n');
    } catch (error) {
        ctx.status = 400;
        ctx.body = 'Error processing zip file: ' + error.message;
    }
});

const streamToString = (stream) => {
    return new Promise((resolve, reject) => {
        const chunks = [];
        stream.on('data', chunk => chunks.push(chunk));
        stream.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
        stream.on('error', reject);
    });
};

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});