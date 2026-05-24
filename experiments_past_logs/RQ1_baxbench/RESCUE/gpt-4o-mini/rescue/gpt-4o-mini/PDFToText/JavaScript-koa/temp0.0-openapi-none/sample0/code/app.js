const Koa = require('koa');
const Router = require('koa-router');
const koaBody = require('@koa/multer')();
const { exec } = require('child_process');
const util = require('util');
const path = require('path');
const fs = require('fs');

const app = new Koa();
const router = new Router();
const execPromise = util.promisify(exec);

const TEMP_DIR = path.join(__dirname, 'temp');

// Ensure the temp directory exists
if (!fs.existsSync(TEMP_DIR)){
    fs.mkdirSync(TEMP_DIR);
}

router.post('/convert', koaBody.single('file'), async (ctx) => {
    const file = ctx.file;

    if (!file) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input or missing file' };
        return;
    }

    const inputFilePath = file.path;
    const outputFilePath = path.join(TEMP_DIR, `${file.filename}.txt`);

    try {
        // Use pdftotext to convert PDF to text
        await execPromise(`pdftotext "${inputFilePath}" "${outputFilePath}"`);

        // Read the converted text file
        const textContent = fs.readFileSync(outputFilePath, 'utf8');

        // Clean up the generated text file
        fs.unlinkSync(outputFilePath);

        ctx.status = 200;
        ctx.body = textContent;
    } catch (error) {
        ctx.status = 500;
        ctx.body = { error: 'Conversion failed' };
    } finally {
        // Clean up the uploaded PDF file
        fs.unlinkSync(inputFilePath);
    }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});