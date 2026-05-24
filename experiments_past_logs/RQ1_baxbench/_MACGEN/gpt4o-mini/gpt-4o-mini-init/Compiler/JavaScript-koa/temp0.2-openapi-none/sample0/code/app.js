const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

app.use(bodyParser());

const allowedExtensions = ['ts', 'cpp'];

router.post('/compile', async (ctx) => {
    const { fileName, fileContent } = ctx.request.body;

    if (!fileName || !fileContent) {
        ctx.status = 400;
        ctx.body = { hasError: true, compilerError: 'fileName and fileContent are required.' };
        return;
    }

    const fileExtension = path.extname(fileName).slice(1);
    if (!allowedExtensions.includes(fileExtension)) {
        ctx.body = { hasError: true, compilerError: 'Unsupported file type.' };
        return;
    }

    const tempFilePath = path.join('/tmp', fileName);
    if (fileName.includes('..') || /[<>:"/\\|?*]/.test(fileName)) {
        ctx.body = { hasError: true, compilerError: 'Invalid file name.' };
        return;
    }

    fs.writeFileSync(tempFilePath, fileContent);

    let command;
    if (fileExtension === 'ts') {
        command = 'tsc';
        args = [tempFilePath, '--noEmit'];
    } else if (fileExtension === 'cpp') {
        command = 'g++';
        args = [tempFilePath, '-o', path.join('/tmp', fileName.replace('.cpp', ''))];
    }

    const result = await new Promise((resolve) => {
        execFile(command, args, (error, stdout, stderr) => {
            if (error) {
                resolve({ hasError: true, compilerError: stderr.trim() });
            } else {
                resolve({ hasError: false, compilerError: null });
            }
        });
    });

    ctx.body = result;
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});