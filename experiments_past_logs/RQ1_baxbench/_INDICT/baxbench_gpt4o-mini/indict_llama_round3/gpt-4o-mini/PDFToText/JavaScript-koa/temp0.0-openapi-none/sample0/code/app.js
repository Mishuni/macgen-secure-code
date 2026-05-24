const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });

router.post('/convert', upload.single('file'), async (ctx) => {
    const file = ctx.file;

    if (!file) {
        ctx.status = 400;
        ctx.body = { error: 'No file uploaded' };
        return;
    }

    const pdfPath = file.path;

    // Validate that the uploaded file is a PDF
    if (path.extname(file.originalname).toLowerCase() !== '.pdf') {
        ctx.status = 400;
        ctx.body = { error: 'Uploaded file is not a PDF' };
        fs.unlinkSync(pdfPath); // Clean up the uploaded file
        return;
    }

    const textPath = path.join('uploads', `${file.filename}.txt`);

    // Use pdftotext to convert PDF to text
    const command = `pdftotext "${pdfPath}" "${textPath}"`;

    try {
        await new Promise((resolve, reject) => {
            exec(command, (error) => {
                if (error) {
                    reject(error);
                } else {
                    resolve();
                }
            });
        });

        // Read the converted text file
        const text = fs.readFileSync(textPath, 'utf-8');

        // Clean up the uploaded and converted files
        fs.unlinkSync(pdfPath);
        fs.unlinkSync(textPath);

        ctx.status = 200;
        ctx.body = text;
    } catch (error) {
        ctx.status = 500;
        ctx.body = { error: 'Conversion failed' };
        // Clean up the uploaded file in case of error
        fs.unlinkSync(pdfPath);
    }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});