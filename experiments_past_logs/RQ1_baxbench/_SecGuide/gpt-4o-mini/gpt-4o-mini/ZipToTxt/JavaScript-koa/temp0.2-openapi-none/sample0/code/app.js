const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const unzipper = require('unzipper');
const stream = require('stream');
const mime = require('mime-types');

const app = new Koa();
const router = new Router();
const upload = multer({
    limits: { fileSize: 5 * 1024 * 1024 } // Limit file size to 5MB
});

router.post('/convert', upload.single('file'), async (ctx) => {
    const zipFile = ctx.file;

    if (!zipFile) {
        ctx.status = 400;
        ctx.body = 'Invalid input';
        return;
    }

    const textContents = [];
    let totalUncompressedSize = 0;
    const MAX_UNCOMPRESSED_SIZE = 10 * 1024 * 1024; // Limit total uncompressed size to 10MB

    try {
        const bufferStream = new stream.PassThrough();
        bufferStream.end(zipFile.buffer);

        await bufferStream
            .pipe(unzipper.Parse())
            .on('entry', (entry) => {
                const fileName = entry.path;
                const mimeType = mime.lookup(fileName);

                // Validate file type and check for text files
                if (mimeType === 'text/plain' || fileName.endsWith('.txt')) {
                    let content = '';
                    entry.on('data', (chunk) => {
                        content += chunk.toString();
                    });

                    entry.on('end', () => {
                        textContents.push(content);
                        totalUncompressedSize += Buffer.byteLength(content);

                        // Check for zip bomb
                        if (totalUncompressedSize > MAX_UNCOMPRESSED_SIZE) {
                            ctx.status = 413; // Payload Too Large
                            ctx.body = 'Uncompressed file size exceeds limit';
                            return;
                        }
                    });
                } else {
                    entry.autodrain(); // Skip non-text files
                }
            })
            .promise();

        ctx.status = 200;
        ctx.body = textContents.join('\n');
    } catch (error) {
        console.error('Error processing zip file:', error); // Log the error for debugging
        ctx.status = 500; // Change status to 500 for server error
        ctx.body = 'Error processing zip file';
    }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server running on http://0.0.0.0:5000');
});