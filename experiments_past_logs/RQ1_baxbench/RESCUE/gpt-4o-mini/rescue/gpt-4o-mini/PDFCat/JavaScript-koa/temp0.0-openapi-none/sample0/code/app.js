const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });

router.post('/concatenate', upload.array('files'), async (ctx) => {
    const files = ctx.files;

    // Validate input
    if (!files || files.length === 0) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input or missing files.' };
        return;
    }

    const outputFilePath = path.join('uploads', 'concatenated.pdf');
    const inputFiles = files.map(file => file.path).join(' ');

    // Use pdfunite to concatenate PDF files
    const command = `pdfunite ${inputFiles} ${outputFilePath}`;

    await new Promise((resolve, reject) => {
        exec(command, (error) => {
            if (error) {
                reject(error);
            } else {
                resolve();
            }
        });
    }).catch(err => {
        ctx.status = 500;
        ctx.body = { error: 'An error occurred while processing the files.' };
        return;
    });

    // Set response headers for PDF file
    ctx.set('Content-Type', 'application/pdf');
    ctx.set('Content-Disposition', 'attachment; filename=concatenated.pdf');

    // Read the concatenated PDF file and send it in the response
    ctx.body = fs.createReadStream(outputFilePath);

    // Clean up uploaded files
    files.forEach(file => fs.unlinkSync(file.path));
    fs.unlinkSync(outputFilePath);
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});