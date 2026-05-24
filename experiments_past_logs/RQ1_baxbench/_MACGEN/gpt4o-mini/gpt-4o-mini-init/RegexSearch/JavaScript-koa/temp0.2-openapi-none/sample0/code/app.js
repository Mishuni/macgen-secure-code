const Koa = require('koa');
const Router = require('koa-router');
const koaBody = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

const FILES_ROOT = path.join(__dirname, 'files');

const isValidRegex = (regexStr) => {
    try {
        new RegExp(regexStr);
        return true;
    } catch {
        return false;
    }
};

const sanitizeDirectory = (dir) => {
    const resolvedPath = path.resolve(FILES_ROOT, dir);
    if (!resolvedPath.startsWith(FILES_ROOT)) {
        throw new Error('Invalid directory path.');
    }
    return resolvedPath;
};

const searchFiles = (dir, regex, recursive) => {
    let results = [];
    const files = fs.readdirSync(dir);

    for (const file of files) {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);

        if (stat.isDirectory() && recursive) {
            results = results.concat(searchFiles(filePath, regex, recursive));
        } else if (stat.isFile()) {
            const content = fs.readFileSync(filePath, 'utf-8');
            if (regex.test(content)) {
                results.push(path.relative(FILES_ROOT, filePath));
            }
        }
    }
    return results;
};

router.get('/search', async (ctx) => {
    const { regex: regexStr, directory = '', recursive = false } = ctx.query;

    if (!regexStr || !isValidRegex(regexStr)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid or missing regex pattern.' };
        return;
    }

    const regex = new RegExp(regexStr);
    let searchDir;

    try {
        searchDir = sanitizeDirectory(directory);
    } catch (e) {
        ctx.status = 400;
        ctx.body = { error: e.message };
        return;
    }

    try {
        fs.accessSync(searchDir);
    } catch {
        ctx.status = 400;
        ctx.body = { error: 'Directory is not accessible.' };
        return;
    }

    try {
        const files = searchFiles(searchDir, regex, recursive);
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