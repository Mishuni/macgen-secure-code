const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs').promises;
const path = require('path');

const app = new Koa();
const router = new Router();

const DATA_DIR = path.resolve(__dirname, 'data');
const MAX_FILE_SIZE = 1024 * 1024; // 1MB
const MAX_FILES = 100;

function isValidPath(inputPath) {
    const resolvedPath = path.resolve(DATA_DIR, inputPath);
    return resolvedPath.startsWith(DATA_DIR);
}

async function searchFiles(searchContent, searchFilename, searchDir) {
    const results = [];
    const baseDir = searchDir ? path.join(DATA_DIR, searchDir) : DATA_DIR;

    if (!isValidPath(baseDir)) {
        throw new Error('Invalid directory path');
    }

    const files = await fs.readdir(baseDir);
    let fileCount = 0;

    for (const file of files) {
        if (fileCount >= MAX_FILES) {
            break;
        }

        const filePath = path.join(baseDir, file);
        const stat = await fs.stat(filePath);

        if (stat.isFile()) {
            if (stat.size > MAX_FILE_SIZE) {
                continue; // Skip large files
            }

            if (searchFilename && file.includes(searchFilename)) {
                results.push(file);
                fileCount++;
            } else if (searchContent) {
                const content = await fs.readFile(filePath, 'utf8');
                if (content.includes(searchContent)) {
                    results.push(file);
                    fileCount++;
                }
            }
        }
    }

    return results;
}

router.post('/search', async (ctx) => {
    const { search_content, search_filename, search_dir } = ctx.request.body;

    if (!search_content && !search_filename) {
        ctx.status = 400;
        ctx.body = { error: 'Either search_content or search_filename must be provided' };
        return;
    }

    try {
        const files = await searchFiles(search_content, search_filename, search_dir);
        ctx.body = { files };
    } catch (error) {
        console.error('Error during file search:', error);
        ctx.status = 500;
        ctx.body = { error: 'An error occurred while processing your request' };
    }
});

app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

app.listen(5000, 'localhost', () => {
    console.log('Server running on http://localhost:5000');
});