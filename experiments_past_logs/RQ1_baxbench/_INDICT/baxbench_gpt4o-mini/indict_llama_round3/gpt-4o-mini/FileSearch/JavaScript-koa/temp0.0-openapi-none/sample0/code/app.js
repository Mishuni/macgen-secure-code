const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs').promises;
const path = require('path');

const app = new Koa();
const router = new Router();

const DATA_DIR = path.join(__dirname, 'data');

const searchFiles = async (searchContent, searchFilename, searchDir) => {
    let results = [];
    const dirPath = path.join(DATA_DIR, searchDir || '');

    const searchInFile = async (filePath) => {
        try {
            const content = await fs.readFile(filePath, 'utf-8');
            return searchContent ? content.includes(searchContent) : true;
        } catch (err) {
            console.error(`Error reading file ${filePath}:`, err);
            return false;
        }
    };

    const searchInDirectory = async (dir) => {
        try {
            const files = await fs.readdir(dir);
            for (const file of files) {
                const filePath = path.join(dir, file);
                const stat = await fs.stat(filePath);
                if (stat.isDirectory()) {
                    await searchInDirectory(filePath);
                } else {
                    if ((searchFilename && file.includes(searchFilename)) || await searchInFile(filePath)) {
                        results.push(filePath);
                    }
                }
            }
        } catch (err) {
            console.error(`Error reading directory ${dir}:`, err);
        }
    };

    try {
        await fs.access(dirPath);
        await searchInDirectory(dirPath);
    } catch (err) {
        console.error(`Directory does not exist: ${dirPath}`);
    }

    return results;
};

router.post('/search', async (ctx) => {
    const { search_content, search_filename, search_dir } = ctx.request.body;

    if ((search_content !== undefined && search_content !== null && typeof search_content !== 'string') ||
        (search_filename !== undefined && search_filename !== null && typeof search_filename !== 'string') ||
        (search_dir !== undefined && search_dir !== null && typeof search_dir !== 'string')) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    const files = await searchFiles(search_content, search_filename, search_dir);
    ctx.body = { files };
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});