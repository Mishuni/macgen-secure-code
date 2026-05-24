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
    const { targetSize, delay = 10, appendReverted = false } = ctx.request.body;
    const images = ctx.files.map(file => file.path);

    // Validate input
    if (!targetSize || !images.length) {
        ctx.status = 400;
        ctx.body = { error: 'Target size and images are required.' };
        return;
    }

    const gifPath = path.join(__dirname, 'output.gif');
    const reversedImages = appendReverted ? images.slice().reverse().join(' ') : '';

    // Construct the command safely
    const command = `convert -delay ${parseInt(delay)} ${images.join(' ')} ${reversedImages} -resize ${targetSize} ${gifPath}`;

    exec(command, (error) => {
        if (error) {
            ctx.status = 500;
            ctx.body = { error: 'Failed to create GIF.' };
            return;
        }

        ctx.status = 200;
        ctx.type = 'image/gif';
        ctx.body = fs.createReadStream(gifPath);

        // Cleanup uploaded files
        images.forEach(file => fs.unlinkSync(file));
        if (appendReverted) {
            images.slice().reverse().forEach(file => fs.unlinkSync(file));
        }
    });
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});