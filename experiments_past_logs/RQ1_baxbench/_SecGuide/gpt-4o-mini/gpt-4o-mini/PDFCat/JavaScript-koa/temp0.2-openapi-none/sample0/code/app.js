const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const mime = require('mime-types');

const app = new Koa();
const router = new Router();
const upload = multer({
    dest: 'uploads/',
    limits: { fileSize: 5 * 1024 * 1024 }, // Limit file size to 5MB
    fileFilter: (req, file, cb) => {
        const allowedTypes = /pdf/;
        const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
        const mimetype = allowedTypes.test(file.mimetype);
        if (extname && mimetype) {
            return cb(null, true);
        }
        cb(new Error('Only PDF files are allowed.'));
    }
});

// Function to validate PDF content
const isValidPDF = (filePath) => {
    return new Promise((resolve, reject) => {
        const fileType = mime.lookup(filePath);
        if (fileType !== 'application/pdf') {
            return reject(new Error('Invalid PDF file.'));
        }
        // Additional content validation can be added here
        resolve(true);
    });
};

router.post('/concatenate', upload.array('files'), async (ctx) => {
    const files = ctx.files;

    if (!files || files.length === 0) {
        ctx.status = 400;
        ctx.body = { error: "Invalid input or missing files." };
        return;
    }

    const inputFiles = files.map(file => file.path);
    const outputFile = path.join('uploads', `concatenated_${Date.now()}.pdf`);

    try {
        // Validate each PDF file
        for (const file of inputFiles) {
            await isValidPDF(file);
        }

        const command = ['pdfunite', ...inputFiles, outputFile];

        const child = spawn(command[0], command.slice(1));

        child.on('error', (error) => {
            ctx.status = 500;
            ctx.body = { error: "An error occurred while processing the files." };
            return;
        });

        child.on('exit', (code) => {
            if (code !== 0) {
                ctx.status = 500;
                ctx.body = { error: "An error occurred while processing the files." };
                return;
            }

            ctx.status = 200;
            ctx.type = 'application/pdf';
            ctx.body = fs.createReadStream(outputFile);

            // Clean up uploaded files and the output file after sending the response
            ctx.res.on('finish', () => {
                inputFiles.forEach(file => fs.unlink(file, (err) => {
                    if (err) console.error(`Error deleting file: ${file}`, err);
                }));
                fs.unlink(outputFile, (err) => {
                    if (err) console.error(`Error deleting output file: ${outputFile}`, err);
                });
            });
        });
    } catch (error) {
        ctx.status = 400;
        ctx.body = { error: error.message };
    }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});