const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = new Koa();
const router = new Router();
const upload = multer({ 
    dest: 'uploads/', 
    limits: { fileSize: 5 * 1024 * 1024 } // Limit file size to 5MB
});

router.post('/create-gif', upload.array('images'), async (ctx) => {
    const { targetSize, delay, appendReverted } = ctx.request.body;
    const images = ctx.files.images.map(file => file.path);
    
    // Validate input parameters
    if (!targetSize || !images.length) {
        ctx.status = 400;
        ctx.body = { error: 'Target size and images are required.' };
        return;
    }
    if (!/^\d+x\d+$/.test(targetSize)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid target size format. Use widthxheight.' };
        return;
    }
    if (delay < 0 || isNaN(delay)) {
        ctx.status = 400;
        ctx.body = { error: 'Delay must be a non-negative integer.' };
        return;
    }

    const gifPath = path.join(__dirname, 'output.gif');
    const sanitizedImages = images.map(img => `"${img.replace(/"/g, '\\"')}"`).join(' ');
    const command = `convert -delay ${delay || 10} -resize ${targetSize} ${sanitizedImages} ${appendReverted === 'true' ? ' -reverse ' + sanitizedImages : ''} ${gifPath}`.replace(/[^a-zA-Z0-9_\-\/\.\s]/g, '');

    exec(command, (error) => {
        if (error) {
            ctx.status = 500;
            ctx.body = { error: 'Failed to create GIF.' };
            return;
        }
        ctx.status = 200;
        ctx.type = 'image/gif';
        ctx.body = fs.createReadStream(gifPath);
    });
});

app.use(router.routes()).use(router.allowedMethods());
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});