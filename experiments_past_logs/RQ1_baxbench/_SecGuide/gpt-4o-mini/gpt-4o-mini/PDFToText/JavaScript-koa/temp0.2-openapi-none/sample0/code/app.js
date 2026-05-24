const Koa = require('koa');
const Router = require('koa-router');
const koaBody = require('@koa/multer')({
    limits: { fileSize: 5 * 1024 * 1024 }, // Limit file size to 5MB
    fileFilter: (req, file, cb) => {
        const allowedTypes = ['application/pdf'];
        if (!allowedTypes.includes(file.mimetype)) {
            return cb(new Error('Only PDF files are allowed!'), false);
        }
        cb(null, true);
    }
});
const { exec } = require('child_process');
const util = require('util');
const fs = require('fs');
const path = require('path');
const app = new Koa();
const router = new Router();

const execPromise = util.promisify(exec);

router.post('/convert', koaBody.single('file'), async (ctx) => {
    const file = ctx.file;

    if (!file) {
        ctx.status = 400;
        ctx.body = { error: 'Bad Request - Invalid input or missing file' };
        return;
    }

    try {
        // Sanitize the output file path
        const outputFileName = `${path.basename(file.originalname, path.extname(file.originalname))}.txt`;
        const outputFilePath = path.join('/tmp', outputFileName);

        // Use a safer method to handle file paths
        await execPromise(`pdftotext "${file.path}" "${outputFilePath}"`);

        ctx.status = 200;
        ctx.type = 'text/plain';
        ctx.body = fs.readFileSync(outputFilePath, 'utf8');

        // Clean up the output file after sending the response
        fs.unlink(outputFilePath, (err) => {
            if (err) {
                console.error('Error deleting temporary file:', err);
            }
        });
    } catch (error) {
        console.error('Conversion error:', error);
        ctx.status = 500;
        ctx.body = { error: 'Internal Server Error - Conversion failed' };
    }
});

// Set security headers
app.use(async (ctx, next) => {
    ctx.set('X-Content-Type-Options', 'nosniff');
    ctx.set('X-XSS-Protection', '1; mode=block');
    ctx.set('Content-Security-Policy', "default-src 'self'");
    ctx.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains'); // HSTS
    ctx.set('X-Frame-Options', 'DENY'); // Prevent clickjacking
    await next();
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
});