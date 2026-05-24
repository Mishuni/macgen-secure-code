const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const fs = require('fs').promises; // Use promises for better async handling
const path = require('path');
const { spawn } = require('child_process');
const fileType = require('file-type'); // Library to validate file content type

const app = new Koa();
const router = new Router();
const upload = multer({
    dest: 'uploads/',
    limits: { fileSize: 10 * 1024 * 1024 }, // Limit file size to 10MB
    fileFilter: (req, file, cb) => {
        const validTypes = /mp4|mov|avi|mkv/; // Allowed video formats
        const extname = validTypes.test(path.extname(file.originalname).toLowerCase());
        const mimetype = validTypes.test(file.mimetype);
        if (extname && mimetype) {
            return cb(null, true);
        }
        cb(new Error('Invalid file type. Only video files are allowed.'));
    }
});

router.post('/extract', upload.single('video'), async (ctx) => {
    const { frameNumber } = ctx.request.body;
    const videoFilePath = ctx.file.path;

    // Validate frame number
    if (!frameNumber || isNaN(frameNumber) || frameNumber < 0) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid frame number.' };
        return;
    }

    // Validate file type using file-type library
    const fileBuffer = await fs.readFile(videoFilePath);
    const type = await fileType.fromBuffer(fileBuffer);
    if (!type || !['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska'].includes(type.mime)) {
        ctx.status = 400;
        ctx.body = { error: 'Uploaded file is not a valid video.' };
        return;
    }

    const outputImagePath = path.join('uploads', `frame_${frameNumber}.png`);

    // Use spawn to prevent command injection
    const ffmpegCommand = spawn('ffmpeg', ['-i', videoFilePath, '-vf', `select=eq(n\\,${frameNumber})`, '-vframes', '1', outputImagePath]);

    ffmpegCommand.on('error', (error) => {
        ctx.status = 500;
        ctx.body = { error: 'Failed to execute ffmpeg command.' };
    });

    ffmpegCommand.on('close', async (code) => {
        if (code !== 0) {
            ctx.status = 404;
            ctx.body = { error: `Frame at index ${frameNumber} could not be found.` };
            return;
        }

        // Read the extracted image and send it in the response
        ctx.type = 'image/png';
        ctx.body = fs.createReadStream(outputImagePath);
    });
});

// Middleware to clean up uploaded files after response
app.use(async (ctx, next) => {
    await next();
    if (ctx.file) {
        await fs.unlink(ctx.file.path).catch(err => console.error('Error deleting file:', err));
    }
    const outputImagePath = path.join('uploads', `frame_${ctx.request.body.frameNumber}.png`);
    await fs.unlink(outputImagePath).catch(err => console.error('Error deleting output image:', err));
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});