const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = new Koa();
const router = new Router();
const upload = multer({ 
    limits: { 
        fileSize: 5 * 1024 * 1024, // Limit file size to 5MB
        files: 1 // Limit to 1 file
    },
    fileFilter: (req, file, cb) => {
        // Accept only PDF files
        if (file.mimetype !== 'application/pdf') {
            return cb(new Error('Only PDF files are allowed!'), false);
        }
        cb(null, true);
    }
});

// Endpoint to convert PDF to text
router.post('/convert', upload.single('file'), async (ctx) => {
    if (!ctx.file) {
        ctx.status = 400;
        ctx.body = { error: 'No file uploaded.' };
        return;
    }

    const filePath = ctx.file.path;
    const outputPath = path.join(__dirname, 'output.txt');

    // Execute pdftotext command
    exec(`pdftotext "${filePath}" "${outputPath}"`, (error) => {
        if (error) {
            ctx.status = 500;
            ctx.body = { error: 'Conversion failed.' };
            return;
        }

        // Read the output text file
        fs.readFile(outputPath, 'utf8', (err, data) => {
            if (err) {
                ctx.status = 500;
                ctx.body = { error: 'Failed to read converted text.' };
                return;
            }

            ctx.status = 200;
            ctx.body = data;

            // Clean up the output file
            fs.unlink(outputPath, (unlinkErr) => {
                if (unlinkErr) {
                    console.error('Failed to delete output file:', unlinkErr);
                }
            });
        });
    });
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});