const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();
const BASE_DIR = path.resolve(__dirname, 'data');

app.use(bodyParser());

router.post('/search', async (ctx) => {
    const { search_content, search_filename, search_dir } = ctx.request.body;

    // Validate request body
    if (typeof search_content !== 'string' && search_content !== null ||
        typeof search_filename !== 'string' && search_filename !== null ||
        typeof search_dir !== 'string' && search_dir !== null) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    // Set default values
    const content = search_content || null;
    const filename = search_filename || null;
    const dir = search_dir ? path.join(BASE_DIR, path.normalize(search_dir)) : BASE_DIR;

    // Sanitize and validate the directory path
    if (!dir.startsWith(BASE_DIR)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid directory path' };
        return;
    }

    let foundFiles = [];

    // Search for files
    try {
        const files = fs.readdirSync(dir);
        for (const file of files) {
            const filePath = path.join(dir, file);
            const stats = fs.statSync(filePath);

            if (stats.isFile()) {
                let matchesContent = true;
                let matchesFilename = true;

                if (content) {
                    const fileContent = fs.readFileSync(filePath, 'utf-8');
                    matchesContent = fileContent.includes(content);
                }

                if (filename) {
                    matchesFilename = file === filename;
                }

                if (matchesContent || matchesFilename) {
                    foundFiles.push(filePath);
                }
            }
        }
    } catch (err) {
        ctx.status = 500;
        ctx.body = { error: 'Error reading directory' };
        return;
    }

    ctx.status = 200;
    ctx.body = { files: foundFiles };
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});