const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

router.post('/compile', async (ctx) => {
    const { fileName, fileContent } = ctx.request.body;

    if (!fileName || !fileContent) {
        ctx.status = 400;
        ctx.body = { hasError: true, compilerError: 'fileName and fileContent are required.' };
        return;
    }

    const fileExtension = fileName.split('.').pop();
    const tempFilePath = path.join(__dirname, fileName);

    // Write the file content to a temporary file
    fs.writeFileSync(tempFilePath, fileContent);

    let command;

    if (fileExtension === 'ts') {
        // Compile TypeScript
        command = `tsc ${tempFilePath} --noEmit`;
    } else if (fileExtension === 'cpp') {
        // Compile C++
        command = `g++ ${tempFilePath} -o output && ./output`;
    } else {
        ctx.status = 400;
        ctx.body = { hasError: true, compilerError: 'Unsupported file type. Only .ts and .cpp are allowed.' };
        fs.unlinkSync(tempFilePath); // Clean up the temporary file
        return;
    }

    const result = await new Promise((resolve) => {
        exec(command, (error, stdout, stderr) => {
            // Clean up the temporary file
            fs.unlink(tempFilePath, (unlinkError) => {
                if (unlinkError) {
                    console.error('Error deleting temporary file:', unlinkError);
                }
            });
            if (error) {
                resolve({ hasError: true, compilerError: stderr.trim() });
            } else {
                resolve({ hasError: false, compilerError: null });
            }
        });
    });

    ctx.body = result;
});

app
    .use(bodyParser())
    .use(router.routes())
    .use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});