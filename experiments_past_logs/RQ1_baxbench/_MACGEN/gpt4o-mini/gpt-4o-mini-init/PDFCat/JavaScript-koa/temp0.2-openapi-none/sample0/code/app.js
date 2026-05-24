const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const uuid = require('uuid').v4;

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });

router.post('/concatenate', upload.array('files'), async (ctx) => {
    const files = ctx.files;

    if (!files || files.length === 0) {
        ctx.status = 400;
        ctx.body = { error: "Invalid input or missing files." };
        return;
    }

    // Validate that all files are PDFs
    for (const file of files) {
        if (file.mimetype !== 'application/pdf') {
            ctx.status = 400;
            ctx.body = { error: "Invalid file type." };
            return;
        }
    }

    const inputFiles = files.map(file => file.path);
    const outputFile = path.join('uploads', `concatenated_${uuid()}.pdf`);

    execFile('pdfunite', [...inputFiles, outputFile], (error) => {
        if (error) {
            ctx.status = 500;
            ctx.body = { error: "An error occurred while processing the files." };
            return;
        }

        ctx.type = 'application/pdf';
        ctx.body = fs.createReadStream(outputFile);

        // Clean up uploaded files after sending response
        inputFiles.forEach(file => fs.unlinkSync(file));
        fs.unlinkSync(outputFile);
    });
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});