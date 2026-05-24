const Koa = require('koa');
const Router = require('koa-router');
const koaBody = require('@koa/multer').default();
const unzipper = require('unzipper');
const { Readable } = require('stream');

const app = new Koa();
const router = new Router();

router.post('/convert', koaBody({ dest: 'uploads/' }), async (ctx) => {
    const file = ctx.request.files.file;

    if (!file) {
        ctx.status = 400;
        ctx.body = 'Invalid input';
        return;
    }

    try {
        const textContents = [];

        // Create a readable stream from the uploaded zip file
        const zipStream = Readable.from(file.buffer);

        // Unzip the contents
        zipStream
            .pipe(unzipper.Parse())
            .on('entry', (entry) => {
                const fileName = entry.path;
                const type = entry.type; // 'Directory' or 'File'

                if (type === 'File' && fileName.endsWith('.txt')) {
                    let content = '';
                    entry.on('data', (chunk) => {
                        content += chunk.toString();
                    });
                    entry.on('end', () => {
                        textContents.push(content);
                    });
                } else {
                    entry.autodrain(); // Skip non-text files
                }
            })
            .on('finish', () => {
                // All entries processed, concatenate all text contents
                ctx.body = textContents.join('\n');
                ctx.status = 200;
            })
            .on('error', (err) => {
                ctx.status = 400;
                ctx.body = 'Error processing zip file';
            });
    } catch (error) {
        ctx.status = 400;
        ctx.body = 'Error processing request';
    }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server running on http://0.0.0.0:5000');
});