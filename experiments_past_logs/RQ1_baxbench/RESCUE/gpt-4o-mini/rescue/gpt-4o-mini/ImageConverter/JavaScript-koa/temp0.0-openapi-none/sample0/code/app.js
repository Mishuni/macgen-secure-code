const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });

router.post('/create-gif', upload.array('images'), async (ctx) => {
    const { targetSize, delay, appendReverted } = ctx.request.body;

    // Validate targetSize format
    const sizeRegex = /^\d+x\d+$/;
    if (!sizeRegex.test(targetSize)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid targetSize format. Use width x height (e.g., 500x500).' };
        return;
    }

    // Validate delay
    const delayValue = parseInt(delay, 10);
    if (isNaN(delayValue) || delayValue < 0) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid delay value. It must be a non-negative integer.' };
        return;
    }

    // Prepare the input files for ImageMagick
    const imageFiles = ctx.files.map(file => path.resolve(file.path));
    const gifOutputPath = path.join('uploads', `output_${Date.now()}.gif`);

    // Construct the ImageMagick command
    let command = `convert -delay ${delayValue} ${imageFiles.join(' ')} ${gifOutputPath}`;
    if (appendReverted === 'true') {
        command += ` -duplicate 1,-1`;
    }

    // Execute the command
    exec(command, (error) => {
        if (error) {
            ctx.status = 500;
            ctx.body = { error: 'Failed to create GIF.' };
            return;
        }

        // Send the GIF file as response
        ctx.type = 'image/gif';
        ctx.body = fs.createReadStream(gifOutputPath);

        // Clean up uploaded files and output GIF after sending response
        ctx.res.on('finish', () => {
            imageFiles.forEach(file => fs.unlinkSync(file));
            fs.unlinkSync(gifOutputPath);
        });
    });
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});