const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

const BASE_DIR = path.resolve(__dirname, './files');

function isPathSafe(resolvedPath) {
    return resolvedPath.startsWith(BASE_DIR);
}

function searchFiles(directory, regexPattern, recursive) {
    const results = [];
    const searchDirectory = path.resolve(BASE_DIR, directory || '.');

    function traverseDirectory(dir) {
        const files = fs.readdirSync(dir);
        for (const file of files) {
            const filePath = path.join(dir, file);
            const stats = fs.lstatSync(filePath);
            if (stats.isDirectory() && recursive) {
                traverseDirectory(filePath);
            } else if (stats.isFile()) {
                const content = fs.readFileSync(filePath, 'utf8');
                if (new RegExp(regexPattern).test(content)) {
                    results.push(path.relative(BASE_DIR, filePath));
                }
            }
        }
    }

    traverseDirectory(searchDirectory);
    return results;
}

router.get('/search', async (ctx) => {
    const { regex, directory, recursive } = ctx.query;

    if (!regex) {
        ctx.status = 400;
        ctx.body = { error: 'Missing required query parameter: regex' };
        return;
    }

    try {
        const results = searchFiles(directory, regex, recursive === 'true');
        ctx.status = 200;
        ctx.body = { files: results };
    } catch (error) {
        ctx.status = 500;
        ctx.body = { error: 'Internal server error' };
    }
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});