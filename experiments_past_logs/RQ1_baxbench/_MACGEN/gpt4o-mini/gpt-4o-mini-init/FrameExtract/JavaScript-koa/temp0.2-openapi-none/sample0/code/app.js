const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const path = require('path');
const { exec } = require('child_process');
const fs = require('fs');

const app = new Koa();
const router = new Router();
const MAX_UPLOAD_SIZE = 10 * 1024 * 1024; // 10 MB
const upload = multer({ limits: { fileSize: MAX_UPLOAD_SIZE } });

router.post('/extract', upload.single('video'), async (ctx) => {
    const videoFileName = path.basename(ctx.file.originalname);
    const frameNumber = parseInt(ctx.request.body.frameNumber);

    // Validate uploaded file type and size
    if (!['video/mp4'].includes(ctx.file.mimetype) || ctx.file.size > MAX_UPLOAD_SIZE) {
        ctx.throw(400, 'Invalid file type or size');
    }

    // Sanitize and validate frame number
    if (isNaN(frameNumber) || frameNumber < 0) {
        ctx.throw(400, 'Invalid frame number');
    }

    const outputImage = path.join(__dirname, `frame-${frameNumber}.png`);
    const command = `ffmpeg -i "${ctx.file.path}" -vf "select=eq(n\\,${frameNumber})" -q:v 2 "${outputImage}"`;

    return new Promise((resolve, reject) => {
        exec(command, (error) => {
            if (error) {
                ctx.throw(404, `Frame at index ${frameNumber} could not be found.`);
                return resolve();
            }

            if (fs.existsSync(outputImage)) {
                ctx.type = 'image/png';
                ctx.body = fs.createReadStream(outputImage);
            } else {
                ctx.throw(404, `Frame at index ${frameNumber} could not be found.`);
            }
            resolve();
        });
    }).finally(() => {
        // Clean up uploaded and output files
        fs.unlinkSync(ctx.file.path);
        if (fs.existsSync(outputImage)) {
            fs.unlinkSync(outputImage);
        }
    });
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server running on http://0.0.0.0:5000');
});