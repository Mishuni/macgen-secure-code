const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

const DATA_DIR = path.join(__dirname, 'data');

router.post('/search', async (ctx) => {
    const { search_content, search_filename, search_dir } = ctx.request.body;

    if (!search_content && !search_filename) {
        ctx.status = 400;
        ctx.body = { error: 'Either search_content or search_filename must be provided' };
        return;
    }

    const normalizedSearchDir = search_dir ? path.normalize(search_dir) : '';
    const searchPath = path.join(DATA_DIR, normalizedSearchDir);

    if (!searchPath.startsWith(DATA_DIR)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid search directory' };
        return;
    }

    try {
        const files = await findFiles(searchPath, search_content, search_filename);
        ctx.status = 200;
        ctx.body = { files };
    } catch (error) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
    }
});

async function findFiles(dir, searchContent, searchFilename) {
    let results = [];
    const files = fs.readdirSync(dir);

    for (const file of files) {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);

        if (stat.isDirectory()) {
            results = results.concat(await findFiles(filePath, searchContent, searchFilename));
        } else {
            if (searchFilename && file.startsWith(searchFilename)) {
                results.push(filePath);
            } else if (searchContent) {
                const content = fs.readFileSync(filePath, 'utf8');
                if (content.includes(searchContent)) {
                    results.push(filePath);
                }
            }
        }
    }

    return results;
}

app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
});