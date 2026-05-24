const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const sharp = require('sharp'); // Using sharp for image processing
const path = require('path');
const fs = require('fs');
const os = require('os');

const app = new Koa();
const router = new Router();
const upload = multer({
    dest: 'uploads/',
    fileFilter: (req, file, cb) => {
        const allowedTypes = /jpeg|jpg|png|gif/;
        const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
        const mimetype = allowedTypes.test(file.mimetype);

        if (extname && mimetype) {
            return cb(null, true);
        }
        cb(new Error('Error: File type not allowed!'));
    },
    limits: { fileSize: 5 * 1024 * 1024 } // Limit file size to 5MB
});

router.post('/create-gif', upload.array('images'), async (ctx) => {
    const { targetSize, delay, appendReverted } = ctx.request.body;
    const images = ctx.files.map(file => file.path);

    if (!targetSize || !/^\d+x\d+$/.test(targetSize)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid target size format. Use width x height (e.g., 500x500).' };
        return;
    }

    const gifPath = path.join(os.tmpdir(), 'output.gif'); // Store in a temporary directory

    // Validate delay to ensure it's a number
    const validDelay = parseInt(delay, 10);
    if (isNaN(validDelay) || validDelay < 0) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid delay value. It must be a non-negative number.' };
        return;
    }

    try {
        const imageBuffers = await Promise.all(images.map(image => sharp(image).resize(parseInt(targetSize.split('x')[0]), parseInt(targetSize.split('x')[1])).toBuffer()));

        // Create GIF using sharp
        await sharp({
            create: {
                width: parseInt(targetSize.split('x')[0]),
                height: parseInt(targetSize.split('x')[1]),
                channels: 4,
                background: { r: 255, g: 255, b: 255, alpha: 0 }
            }
        })
        .gif({ delay: validDelay })
        .composite(imageBuffers.map((buffer, index) => ({ input: buffer, blend: 'over' })))
        .toFile(gifPath);

        ctx.status = 200;
        ctx.type = 'image/gif';
        ctx.body = fs.createReadStream(gifPath);
    } catch (error) {
        console.error('Error creating GIF:', error); // Log error internally
        ctx.status = 500;
        ctx.body = { error: 'Failed to create GIF.' };
    } finally {
        // Clean up uploaded files
        images.forEach(image => fs.unlinkSync(image));
        // Optionally, clean up the generated GIF if not needed
        // fs.unlinkSync(gifPath);
    }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server running on http://0.0.0.0:5000');
});