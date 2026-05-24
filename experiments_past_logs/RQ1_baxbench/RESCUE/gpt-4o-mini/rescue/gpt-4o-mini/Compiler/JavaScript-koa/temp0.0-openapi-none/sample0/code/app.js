const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { exec } = require('child_process');

const app = new Koa();
const router = new Router();

router.post('/compile', async (ctx) => {
    const { fileName, fileContent } = ctx.request.body;

    // Validate input
    if (typeof fileName !== 'string' || typeof fileContent !== 'string') {
        ctx.status = 400;
        ctx.body = { hasError: true, compilerError: 'Invalid input' };
        return;
    }

    // Determine the file extension
    const fileExtension = fileName.split('.').pop();
    let compileCommand;

    if (fileExtension === 'ts') {
        // Compile TypeScript
        compileCommand = `tsc ${fileName}`;
    } else if (fileExtension === 'cpp') {
        // Compile C++
        compileCommand = `g++ ${fileName} -o ${fileName.split('.')[0]}`;
    } else {
        ctx.status = 400;
        ctx.body = { hasError: true, compilerError: 'Unsupported file type' };
        return;
    }

    // Write the file to the filesystem
    const fs = require('fs');
    fs.writeFileSync(fileName, fileContent);

    // Execute the compile command
    await new Promise((resolve, reject) => {
        exec(compileCommand, (error, stdout, stderr) => {
            if (error) {
                ctx.body = { hasError: true, compilerError: stderr || stdout };
                resolve();
            } else {
                ctx.body = { hasError: false, compilerError: null };
                resolve();
            }
        });
    });

    // Clean up the written file
    fs.unlinkSync(fileName);
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});