const Koa = require('koa');
const Router = require('koa-router');
const koaBody = require('koa-body');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { error: err.message };
        ctx.app.emit('error', err, ctx);
    }
});

// Search files by regex
router.get('/search', async (ctx) => {
    const { regex, directory, recursive } = ctx.query;

    // Validate regex
    let regexPattern;
    try {
        regexPattern = new RegExp(regex);
    } catch (e) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid regex pattern.' };
        return;
    }

    // Validate directory
    const baseDir = path.join(__dirname, 'files');
    const searchDir = directory ? path.join(baseDir, directory) : baseDir;

    if (!fs.existsSync(searchDir) || !fs.lstatSync(searchDir).isDirectory()) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid directory path.' };
        return;
    }

    const matchingFiles = [];

    // Function to search files
    const searchFiles = (dir) => {
        const files = fs.readdirSync(dir);
        for (const file of files) {
            const filePath = path.join(dir, file);
            if (fs.lstatSync(filePath).isDirectory() && recursive === 'true') {
                searchFiles(filePath);
            } else {
                const content = fs.readFileSync(filePath, 'utf-8');
                if (regexPattern.test(content)) {
                    matchingFiles.push(path.relative(baseDir, filePath));
                }
            }
        }
    };

    searchFiles(searchDir);

    ctx.body = { files: matchingFiles };
});

// Use koa-body for parsing request bodies
app.use(koaBody());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});