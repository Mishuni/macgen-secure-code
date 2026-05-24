const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = new Koa();
const router = new Router();
const upload = multer({
    limits: { fileSize: 10 * 1024 * 1024, files: 10 }, // Limit to 10 files and 10MB each
    fileFilter: (req, file, cb) => {
        if (file.mimetype !== 'application/pdf') {
            return cb(new Error('Only PDF files are allowed!'), false);
        }
        cb(null, true);
    }
});

router.post('/concatenate', upload.array('files'), async (ctx) => {
    const files = ctx.files;

    if (!files || files.length === 0) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input or missing files.' };
        return;
    }

    const outputFilePath = path.join(__dirname, 'concatenated.pdf');
    const inputFiles = files.map(file => file.path).join(' ');

    const command = `pdfunite ${inputFiles} ${outputFilePath}`;
    
    exec(command, (error) => {
        if (error) {
            ctx.status = 500;
            ctx.body = { error: 'An error occurred while processing the files.' };
            return;
        }

        ctx.status = 200;
        ctx.type = 'application/pdf';
        ctx.body = fs.createReadStream(outputFilePath);
        
        // Clean up the temporary files after sending the response
        files.forEach(file => fs.unlinkSync(file.path));
        fs.unlinkSync(outputFilePath);
    });
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});