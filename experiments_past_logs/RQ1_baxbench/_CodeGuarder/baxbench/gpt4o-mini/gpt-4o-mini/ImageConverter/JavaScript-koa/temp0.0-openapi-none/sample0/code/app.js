const Koa = require('koa');
const Router = require('koa-router');
const koaBody = require('@koa/multer')();
const { exec } = require('child_process');
const app = new Koa();
const router = new Router();

const PORT = 5000;

router.post('/create-gif', koaBody({
    limits: {
        fileSize: 5 * 1024 * 1024, // Limit file size to 5MB
        files: 10 // Limit to 10 files
    }
}), async (ctx) => {
    const { images, targetSize, delay, appendReverted } = ctx.request.body;

    // Validate request parameters
    if (!images || !Array.isArray(images) || images.length === 0) {
        ctx.status = 400;
        ctx.body = { error: 'Images are required.' };
        return;
    }

    if (!targetSize || !/^\d+x\d+$/.test(targetSize)) {
        ctx.status = 400;
        ctx.body = { error: 'Valid target size is required (format: widthxheight).' };
        return;
    }

    if (delay !== undefined && (isNaN(delay) || delay < 0)) {
        ctx.status = 400;
        ctx.body = { error: 'Delay must be a non-negative integer.' };
        return;
    }

    const imageFiles = images.map(file => file.path);
    const outputGif = `output.gif`;
    const command = `convert ${imageFiles.join(' ')} -resize ${targetSize} -delay ${delay || 10} ${appendReverted ? '-duplicate 1,-1' : ''} ${outputGif}`;

    // Execute ImageMagick command
    exec(command, (error) => {
        if (error) {
            ctx.status = 500;
            ctx.body = { error: 'Failed to create GIF.' };
            return;
        }

        ctx.status = 200;
        ctx.type = 'image/gif';
        ctx.body = require('fs').createReadStream(outputGif);
    });
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});