const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const multer = require('@koa/multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = new Koa();
const router = new Router();

// Configure multer for file uploads
const upload = multer({
    limits: {
        fileSize: 10 * 1024 * 1024, // Limit file size to 10MB
        files: 1 // Limit to 1 file
    },
    fileFilter: (req, file, cb) => {
        const ext = path.extname(file.originalname).toLowerCase();
        const allowedExtensions = ['.mp4', '.avi', '.mov', '.mkv']; // Allowed video formats
        if (!allowedExtensions.includes(ext)) {
            return cb(new Error('Only video files are allowed!'), false);
        }
        cb(null, true);
    }
});

// POST route to extract frame
router.post('/extract', upload.single('video'), async (ctx) => {
    const { frameNumber } = ctx.request.body;
    const videoFile = ctx.file;

    if (!videoFile) {
        ctx.status = 400;
        ctx.body = { error: 'No video file uploaded.' };
        return;
    }

    const outputImagePath = path.join(__dirname, `frame-${frameNumber}.png`);

    // Construct ffmpeg command
    const ffmpegCommand = `ffmpeg -i ${videoFile.path} -vf "select=eq(n\\,${frameNumber})" -vframes 1 ${outputImagePath}`;

    // Execute ffmpeg command
    exec(ffmpegCommand, (error, stdout, stderr) => {
        if (error) {
            if (stderr.includes('Invalid frame')) {
                ctx.status = 404;
                ctx.body = { error: `Frame at index ${frameNumber} could not be found.` };
            } else {
                ctx.status = 500;
                ctx.body = { error: 'An error occurred while processing the video.' };
            }
            return;
        }

        // Send the extracted image as a response
        ctx.status = 200;
        ctx.type = 'image/png';
        ctx.body = fs.createReadStream(outputImagePath);

        // Clean up the uploaded video and output image
        fs.unlink(videoFile.path, (err) => {
            if (err) console.error('Error deleting video file:', err);
        });
        fs.unlink(outputImagePath, (err) => {
            if (err) console.error('Error deleting output image:', err);
        });
    });
});

// Middleware
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});