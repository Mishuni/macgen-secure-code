const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

// Define the base data directory
const BASE_DATA_DIR = path.resolve(__dirname, 'data');

// Utility function to sanitize and validate input paths
function sanitizeAndValidatePath(inputPath) {
    if (!inputPath) {
        return BASE_DATA_DIR; // Default to the base directory if no path is provided
    }

    const resolvedPath = path.resolve(BASE_DATA_DIR, inputPath);

    // Ensure the resolved path is within the allowed base directory
    if (!resolvedPath.startsWith(BASE_DATA_DIR)) {
        throw new Error('Invalid directory path');
    }

    return resolvedPath;
}

// Utility function to search for files by content or filename
function searchFiles(searchDir, searchContent, searchFilename) {
    const resultFiles = [];

    // Recursively search through the directory
    function searchDirectory(directory) {
        const files = fs.readdirSync(directory);

        for (const file of files) {
            const filePath = path.join(directory, file);
            const stat = fs.statSync(filePath);

            if (stat.isDirectory()) {
                // Recursively search subdirectories
                searchDirectory(filePath);
            } else if (stat.isFile()) {
                // Check for filename match
                if (searchFilename && file.includes(searchFilename)) {
                    resultFiles.push(filePath);
                }

                // Check for content match
                if (searchContent) {
                    const content = fs.readFileSync(filePath, 'utf8');
                    if (content.includes(searchContent)) {
                        resultFiles.push(filePath);
                    }
                }
            }
        }
    }

    searchDirectory(searchDir);
    return resultFiles;
}

// POST /search endpoint
router.post('/search', async (ctx) => {
    try {
        const { search_content: searchContent, search_filename: searchFilename, search_dir: searchDir } = ctx.request.body;

        // Validate input types
        if (searchContent && typeof searchContent !== 'string') {
            ctx.status = 400;
            ctx.body = { error: 'Invalid search_content type' };
            return;
        }

        if (searchFilename && typeof searchFilename !== 'string') {
            ctx.status = 400;
            ctx.body = { error: 'Invalid search_filename type' };
            return;
        }

        if (searchDir && typeof searchDir !== 'string') {
            ctx.status = 400;
            ctx.body = { error: 'Invalid search_dir type' };
            return;
        }

        // Sanitize and validate the search directory
        const sanitizedDir = sanitizeAndValidatePath(searchDir);

        // Perform the file search
        const files = searchFiles(sanitizedDir, searchContent, searchFilename);

        // Respond with the list of matching files
        ctx.status = 200;
        ctx.body = { files };
    } catch (error) {
        ctx.status = 400;
        ctx.body = { error: error.message };
    }
});

// Middleware
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
});