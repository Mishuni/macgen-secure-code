const Koa = require('koa');
const Router = require('koa-router');
const koaBody = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

const FILES_ROOT = path.join(__dirname, 'files');

const searchFiles = (dir, regex, recursive) => {
    let results = [];
    const files = fs.readdirSync(dir);

    for (const file of files) {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);

        if (stat.isDirectory() && recursive) {
            results = results.concat(searchFiles(filePath, regex, recursive));
        } else if (stat.isFile()) {
            try {
                const content = fs.readFileSync(filePath, 'utf-8');
                if (regex.test(content)) {
                    results.push(path.relative(FILES_ROOT, filePath));
                }
            } catch (err) {
                console.error(`Error reading file ${filePath}: ${err.message}`);
            }
        }
    }

    return results;
};

router.get('/search', async (ctx) => {
    const { regex: regexStr, directory = '', recursive = 'false' } = ctx.query;

    if (!regexStr) {
        ctx.status = 400;
        ctx.body = { error: 'Regex pattern is required.' };
        return;
    }

    let regex;
    try {
        regex = new RegExp(regexStr);
    } catch (e) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid regex pattern.' };
        return;
    }

    const searchDir = path.join(FILES_ROOT, directory);
    if (!searchDir.startsWith(FILES_ROOT) || !fs.existsSync(searchDir) || !fs.statSync(searchDir).isDirectory()) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid directory path.' };
        return;
    }

    const isRecursive = recursive === 'true';

    try {
        const files = searchFiles(searchDir, regex, isRecursive);
        ctx.body = { files };
    } catch (e) {
        ctx.status = 500;
        ctx.body = { error: 'Internal server error.' };
    }
});

app
    .use(koaBody())
    .use(router.routes())
    .use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});