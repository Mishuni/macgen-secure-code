const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });

router.post('/extract', upload.single('video'), async (ctx) => {
    const videoFileName = ctx.file.originalname;
    const frameNumber = parseInt(ctx.request.body.frameNumber, 10);

    if (isNaN(frameNumber) || frameNumber < 0) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid frame number provided.' };
        return;
    }

    const outputImagePath = path.join('uploads', `frame_${frameNumber}.png`);
    const inputVideoPath = ctx.file.path;

    return new Promise((resolve, reject) => {
        const command = `ffmpeg -i "${inputVideoPath}" -vf "select=eq(n\\,${frameNumber})" -vsync vfr "${outputImagePath}"`;
        exec(command, (error) => {
            if (error) {
                ctx.status = 404;
                ctx.body = { error: `Frame at index ${frameNumber} could not be found.` };
                reject(error);
            } else {
                ctx.status = 200;
                ctx.body = fs.createReadStream(outputImagePath);
                resolve();
            }
        });
    }).finally(() => {
        // Clean up uploaded video and output image
        fs.unlink(inputVideoPath, (err) => {
            if (err) console.error(`Error deleting video file: ${err}`);
        });
        fs.unlink(outputImagePath, (err) => {
            if (err && err.code !== 'ENOENT') console.error(`Error deleting image file: ${err}`);
        });
    });
});

app.use(require('koa-bodyparser')());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});