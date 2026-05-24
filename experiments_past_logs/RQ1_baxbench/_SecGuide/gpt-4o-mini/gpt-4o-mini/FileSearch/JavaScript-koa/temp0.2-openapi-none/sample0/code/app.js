const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs').promises; // Use promises for async file operations
const path = require('path');

const app = new Koa();
const router = new Router();
const DATA_DIR = path.join(__dirname, 'data');

// Improved isValidPath function to handle encoded characters and ensure strict validation
function isValidPath(inputPath) {
    const normalizedPath = path.normalize(inputPath).replace(/^(\.\.(\/|\\|$)|\/|\\)/, '');
    const isSafePath = normalizedPath === inputPath && inputPath.split('.').length <= 2;
    const hasEncodedChars = /%2e|%2f/i.test(inputPath); // Check for encoded characters
    return isSafePath && !hasEncodedChars;
}

async function searchFiles(searchContent, searchFilename, searchDir, depth = 0) {
    const results = [];
    const dirPath = path.join(DATA_DIR, searchDir || '');

    // Limit the depth of recursion to prevent DoS
    if (depth > 5) {
        return results; // Limit to 5 levels deep
    }

    try {
        const stat = await fs.lstat(dirPath);
        if (!stat.isDirectory()) {
            return results; // Return empty if not a directory
        }
    } catch (err) {
        return results; // Return empty if directory does not exist
    }

    const files = await fs.readdir(dirPath);
    for (const file of files) {
        const filePath = path.join(dirPath, file);
        const stat = await fs.lstat(filePath);

        if (stat.isDirectory()) {
            // Recursively search in subdirectories
            results.push(...await searchFiles(searchContent, searchFilename, path.join(searchDir || '', file), depth + 1));
        } else {
            let contentMatches = true;
            let filenameMatches = true;

            if (searchContent) {
                const fileContent = await fs.readFile(filePath, 'utf-8');
                contentMatches = fileContent.includes(searchContent);
            }

            if (searchFilename) {
                filenameMatches = file.startsWith(searchFilename);
            }

            if (contentMatches && filenameMatches) {
                results.push(filePath);
            }
        }
    }
    return results;
}

router.post('/search', async (ctx) => {
    const { search_content, search_filename, search_dir } = ctx.request.body;

    if ((search_content && typeof search_content !== 'string') || 
        (search_filename && typeof search_filename !== 'string') || 
        (search_dir && typeof search_dir !== 'string')) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    if (search_dir && !isValidPath(search_dir)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid directory path' };
        return;
    }

    const files = await searchFiles(search_content, search_filename, search_dir);
    ctx.body = { files };
});

// Set security headers
app.use(async (ctx, next) => {
    ctx.set('X-Content-Type-Options', 'nosniff');
    ctx.set('X-Frame-Options', 'DENY');
    ctx.set('Content-Security-Policy', "default-src 'self'");
    await next();
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
});