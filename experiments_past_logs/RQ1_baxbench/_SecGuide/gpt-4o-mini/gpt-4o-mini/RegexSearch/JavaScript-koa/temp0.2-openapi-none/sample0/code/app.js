const Koa = require('koa');
const Router = require('koa-router');
const koaBody = require('koa-bodyparser');
const fs = require('fs').promises; // Use promises for async file operations
const path = require('path');
const sanitize = require('sanitize-filename'); // Sanitize input
const helmet = require('koa-helmet'); // For setting security headers

const app = new Koa();
const router = new Router();

const FILES_ROOT = path.join(__dirname, 'files');

// Function to validate regex patterns
function isValidRegex(pattern) {
    try {
        new RegExp(pattern);
        return true;
    } catch (e) {
        return false;
    }
}

function isValidPath(directory) {
    // Ensure the directory is a valid path within FILES_ROOT
    const normalizedPath = path.normalize(path.join(FILES_ROOT, directory));
    return normalizedPath.startsWith(FILES_ROOT) && !normalizedPath.includes('..');
}

async function searchFiles(directory, regexPattern, recursive) {
    const results = [];
    const fullPath = path.join(FILES_ROOT, directory);

    async function search(dir) {
        const files = await fs.readdir(dir);
        for (const file of files) {
            const filePath = path.join(dir, file);
            const stat = await fs.stat(filePath);
            if (stat.isDirectory() && recursive) {
                await search(filePath);
            } else if (stat.isFile()) {
                const content = await fs.readFile(filePath, 'utf-8');
                try {
                    const regex = new RegExp(regexPattern);
                    if (regex.test(content)) {
                        results.push(path.relative(FILES_ROOT, filePath));
                    }
                } catch (e) {
                    // Handle regex error
                    console.error('Invalid regex pattern:', e);
                }
            }
        }
    }

    await search(fullPath);
    return results;
}

router.get('/search', async (ctx) => {
    const { regex, directory = '', recursive = false } = ctx.query;

    if (!regex || !isValidPath(directory) || !isValidRegex(regex)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input: malformed regex or inaccessible directory.' };
        return;
    }

    try {
        const sanitizedRegex = sanitize(regex); // Sanitize regex input
        const files = await searchFiles(directory, sanitizedRegex, recursive === 'true');
        ctx.status = 200;
        ctx.body = { files };
    } catch (error) {
        console.error('Error during file search:', error); // Log error for debugging
        ctx.status = 500;
        ctx.body = { error: 'Internal server error.' };
    }
});

// Use helmet to set security-related HTTP headers
app.use(helmet());
app.use(koaBody());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
});