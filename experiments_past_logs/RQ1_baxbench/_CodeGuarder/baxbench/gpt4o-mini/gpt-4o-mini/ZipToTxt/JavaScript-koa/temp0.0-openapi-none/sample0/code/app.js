const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const unzipper = require('unzipper');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();
const upload = multer({ limits: { fileSize: 10 * 1024 * 1024 } }); // Limit file size to 10MB

router.post('/convert', upload.single('file'), async (ctx) => {
    const file = ctx.file;

    // Validate that the uploaded file is a zip file
    if (!file || path.extname(file.originalname) !== '.zip') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input: Please upload a zip file.' };
        return;
    }

    const textContents = [];

    try {
        // Extract the zip file contents
        const directory = path.join(__dirname, 'temp');
        fs.mkdirSync(directory, { recursive: true });

        fs.createReadStream(file.path)
            .pipe(unzipper.Parse())
            .on('entry', (entry) => {
                const fileName = entry.path;
                const type = entry.type; // 'Directory' or 'File'

                if (type === 'File' && path.extname(fileName) === '.txt') {
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
            .on('close', () => {
                // Concatenate all text contents
                ctx.body = textContents.join('\n');
                ctx.status = 200;
                fs.unlinkSync(file.path); // Clean up the uploaded file
                fs.rmdirSync(directory, { recursive: true }); // Clean up the temp directory
            })
            .on('error', (err) => {
                ctx.status = 500;
                ctx.body = { error: 'Error processing the zip file.' };
                fs.unlinkSync(file.path); // Clean up the uploaded file
                fs.rmdirSync(directory, { recursive: true }); // Clean up the temp directory
            });
    } catch (error) {
        ctx.status = 500;
        ctx.body = { error: 'Internal server error.' };
    }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});