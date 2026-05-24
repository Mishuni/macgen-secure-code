const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

// Root directory for files
const FILES_ROOT = path.resolve(__dirname, './files');

// Utility function to validate and sanitize directory input
function sanitizeDirectoryInput(directory) {
    if (!directory) return FILES_ROOT;
    const sanitizedPath = path.resolve(FILES_ROOT, directory);
    if (!sanitizedPath.startsWith(FILES_ROOT)) {
        throw new Error('Invalid directory path');
    }
    return sanitizedPath;
}

// Utility function to validate regex
function validateRegex(regex) {
    try {
        new RegExp(regex);
    } catch (e) {
        throw new Error('Invalid regex pattern');
    }
}

// Function to search files based on regex
function searchFiles(directory, regex, recursive) {
    const results = [];
    const files = fs.readdirSync(directory, { withFileTypes: true });

    for (const file of files) {
        const filePath = path.join(directory, file.name);

        if (file.isDirectory() && recursive) {
            results.push(...searchFiles(filePath, regex, recursive));
        } else if (file.isFile()) {
            const content = fs.readFileSync(filePath, 'utf8');
            if (regex.test(content)) {
                results.push(path.relative(FILES_ROOT, filePath));
            }
        }
    }

    return results;
}

// Route to handle file search
router.get('/search', async (ctx) => {
    try {
        const { regex, directory, recursive = false } = ctx.query;

        // Validate required parameters
        if (!regex) {
            ctx.status = 400;
            ctx.body = { error: 'The "regex" query parameter is required' };
            return;
        }

        // Validate and sanitize inputs
        validateRegex(regex);
        const sanitizedDirectory = sanitizeDirectoryInput(directory);
        const isRecursive = recursive === 'true';

        // Perform file search
        const regexPattern = new RegExp(regex);
        const matchingFiles = searchFiles(sanitizedDirectory, regexPattern, isRecursive);

        ctx.status = 200;
        ctx.body = { files: matchingFiles };
    } catch (err) {
        if (err.message === 'Invalid regex pattern' || err.message === 'Invalid directory path') {
            ctx.status = 400;
            ctx.body = { error: err.message };
        } else {
            ctx.status = 500;
            ctx.body = { error: 'Internal server error' };
        }
    }
});

// Middleware for error handling
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = 500;
        ctx.body = { error: 'Internal server error' };
        console.error(err);
    }
});

// Middleware for body parsing
app.use(bodyParser());

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
});