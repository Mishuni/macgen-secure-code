const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const uuid = require('uuid');

const app = new Koa();
const router = new Router();
const upload = multer({ 
    dest: 'uploads/', 
    limits: { fileSize: 5 * 1024 * 1024 } // Limit to 5MB
});

router.post('/convert', upload.single('file'), async (ctx) => {
    const file = ctx.file;

    if (!file) {
        ctx.status = 400;
        ctx.body = { error: 'Bad Request - Invalid input or missing file' };
        return;
    }

    // Validate file type
    if (file.mimetype !== 'application/pdf') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid file type. Only PDF files are allowed.' };
        return;
    }

    const safeFileName = `${uuid.v4()}.pdf`;
    const outputFilePath = path.join('uploads', `${uuid.v4()}.txt`);

    try {
        await new Promise((resolve, reject) => {
            exec(`pdftotext "${path.resolve(file.path)}" "${outputFilePath}"`, (error) => {
                if (error) {
                    reject(error);
                } else {
                    resolve();
                }
            });
        });

        const text = fs.readFileSync(outputFilePath, 'utf-8');
        ctx.status = 200;
        ctx.body = text;

        // Clean up files
        fs.unlinkSync(file.path);
        fs.unlinkSync(outputFilePath);
    } catch (error) {
        ctx.status = 500;
        ctx.body = { error: 'Internal Server Error - Conversion failed' };
    }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});