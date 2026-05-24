const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const fs = require('fs');
const { exec } = require('child_process');
const path = require('path');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });

router.post('/extract', upload.single('video'), async (ctx) => {
    const { frameNumber } = ctx.request.body;
    const videoFilePath = ctx.file.path;
    const outputImagePath = path.join('uploads', `frame_${frameNumber}.png`);

    // Validate frameNumber
    const frameNum = parseInt(frameNumber, 10);
    if (isNaN(frameNum) || frameNum < 0) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid frame number provided.' };
        return;
    }

    // Construct the ffmpeg command
    const ffmpegCommand = `ffmpeg -i "${videoFilePath}" -vf "select=eq(n\\,${frameNum})" -vsync vfr "${outputImagePath}"`;

    // Execute the ffmpeg command
    exec(ffmpegCommand, (error) => {
        if (error) {
            ctx.status = 404;
            ctx.body = { error: `Frame at index ${frameNum} could not be found.` };
            return;
        }

        // Read the extracted image and send it as response
        ctx.type = 'image/png';
        ctx.body = fs.createReadStream(outputImagePath);

        // Clean up: remove the uploaded video and extracted image after sending response
        fs.unlink(videoFilePath, (err) => {
            if (err) console.error('Error deleting video file:', err);
        });
        fs.unlink(outputImagePath, (err) => {
            if (err) console.error('Error deleting image file:', err);
        });
    });
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});