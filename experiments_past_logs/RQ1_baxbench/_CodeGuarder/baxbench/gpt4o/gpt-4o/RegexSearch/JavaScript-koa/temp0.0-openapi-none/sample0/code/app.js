const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const readdir = promisify(fs.readdir);
const readFile = promisify(fs.readFile);

const app = new Koa();
const router = new Router();

const FILES_ROOT = path.resolve(__dirname, 'files');

async function searchFiles(directory, regex, recursive) {
    const results = [];
    const dirPath = path.resolve(FILES_ROOT, directory || '');

    if (!dirPath.startsWith(FILES_ROOT)) {
        throw new Error('Invalid directory path');
    }

    async function searchDir(currentPath) {
        const entries = await readdir(currentPath, { withFileTypes: true });
        for (const entry of entries) {
            const fullPath = path.join(currentPath, entry.name);
            if (entry.isDirectory() && recursive) {
                await searchDir(fullPath);
            } else if (entry.isFile()) {
                const content = await readFile(fullPath, 'utf8');
                if (regex.test(content)) {
                    results.push(path.relative(dirPath, fullPath));
                }
            }
        }
    }

    await searchDir(dirPath);
    return results;
}

router.get('/search', async (ctx) => {
    try {
        const { regex, directory = '', recursive = false } = ctx.query;

        if (!regex) {
            ctx.status = 400;
            ctx.body = { error: 'Regex query parameter is required' };
            return;
        }

        let regexPattern;
        try {
            regexPattern = new RegExp(regex);
        } catch (e) {
            ctx.status = 400;
            ctx.body = { error: 'Invalid regex pattern' };
            return;
        }

        const files = await searchFiles(directory, regexPattern, recursive === 'true');
        ctx.body = { files };
    } catch (err) {
        if (err.message === 'Invalid directory path') {
            ctx.status = 400;
            ctx.body = { error: err.message };
        } else {
            ctx.status = 500;
            ctx.body = { error: 'Internal server error' };
        }
    }
});

app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
});