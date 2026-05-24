const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const unzipper = require('unzipper');
const stream = require('stream');

const app = new Koa();
const router = new Router();
const upload = multer({ limits: { fileSize: 10 * 1024 * 1024 } }); // Limit to 10MB

const MAX_FILES = 100; // Maximum number of text files
const MAX_TOTAL_SIZE = 5 * 1024 * 1024; // Maximum total size of text files (5MB)

router.post('/convert', upload.single('file'), async (ctx) => {
    const zipFile = ctx.file;

    // Validate uploaded file type and size
    if (!zipFile || zipFile.mimetype !== 'application/zip' || zipFile.size === 0) {
        ctx.throw(400, 'Invalid file type or size');
    }

    const textContents = [];
    let totalSize = 0;

    try {
        const bufferStream = new stream.PassThrough();
        bufferStream.end(zipFile.buffer);

        await bufferStream
            .pipe(unzipper.Parse())
            .on('entry', (entry) => {
                if (entry.path.endsWith('.txt')) {
                    let content = '';
                    entry.on('data', (chunk) => {
                        content += chunk.toString();
                    });
                    entry.on('end', () => {
                        textContents.push(content);
                        totalSize += Buffer.byteLength(content);

                        // Limit resource usage
                        if (textContents.length > MAX_FILES || totalSize > MAX_TOTAL_SIZE) {
                            ctx.throw(400, 'Too many files or excessive size');
                        }
                    });
                } else {
                    entry.autodrain(); // Discard non-text files
                }
            })
            .promise();

        ctx.status = 200;
        ctx.body = textContents.join('\n');
    } catch (error) {
        ctx.throw(400, 'Invalid input');
    }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});