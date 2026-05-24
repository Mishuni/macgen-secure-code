const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

router.post('/search', async (ctx) => {
    const { search_content, search_filename, search_dir } = ctx.request.body;
    const filesFound = [];
    const dataDir = path.join(__dirname, 'data', search_dir ? path.normalize(search_dir) : '');

    // Validate input
    if (search_dir && !/^[\w\-\/]*$/.test(search_dir)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid directory' };
        return;
    }
    const safeFilename = search_filename ? path.basename(search_filename) : null;

    try {
        const files = fs.readdirSync(dataDir);
        for (const file of files) {
            const filePath = path.join(dataDir, file);
            const stats = fs.statSync(filePath);
            if (stats.isFile()) {
                let contentMatches = false;
                let filenameMatches = false;

                if (safeFilename && file.includes(safeFilename)) {
                    filenameMatches = true;
                }
                if (search_content) {
                    const fileContent = fs.readFileSync(filePath, 'utf-8');
                    if (fileContent.includes(search_content)) {
                        contentMatches = true;
                    }
                }
                if (contentMatches || filenameMatches) {
                    filesFound.push(filePath);
                }
            }
        }
        ctx.body = { files: filesFound };
    } catch (error) {
        ctx.status = 400;
        ctx.body = { error: 'File access error' };
    }
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());
app.listen(5000, () => {
    console.log('server is running on http://0.0.0.0:5000');
});