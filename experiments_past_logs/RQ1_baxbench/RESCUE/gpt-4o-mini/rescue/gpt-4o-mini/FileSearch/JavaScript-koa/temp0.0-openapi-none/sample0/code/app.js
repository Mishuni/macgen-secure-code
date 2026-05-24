const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

// Sanitize and validate the search directory
function sanitizePath(inputPath) {
    const safeBase = path.resolve('/data');
    const resolvedPath = path.resolve(safeBase, inputPath || '');
    if (!resolvedPath.startsWith(safeBase)) {
        throw new Error('Invalid directory path');
    }
    return resolvedPath;
}

// Search for files
async function searchFiles(searchDir, searchContent, searchFilename) {
    const results = [];
    const dirPath = sanitizePath(searchDir);

    const files = fs.readdirSync(dirPath);
    for (const file of files) {
        const filePath = path.join(dirPath, file);
        if (fs.statSync(filePath).isFile()) {
            let contentMatches = true;
            let filenameMatches = true;

            if (searchContent) {
                const content = fs.readFileSync(filePath, 'utf-8');
                contentMatches = content.includes(searchContent);
            }

            if (searchFilename) {
                filenameMatches = file.includes(searchFilename);
            }

            if (contentMatches && filenameMatches) {
                results.push(filePath);
            }
        }
    }
    return results;
}

// API endpoint
router.post('/search', async (ctx) => {
    const { search_content, search_filename, search_dir } = ctx.request.body;

    try {
        const files = await searchFiles(search_dir, search_content, search_filename);
        ctx.body = { files };
    } catch (error) {
        ctx.status = 400;
        ctx.body = { error: error.message };
    }
});

// Middleware
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});