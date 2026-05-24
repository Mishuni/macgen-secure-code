const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { exec } = require('child_process');

const app = new Koa();
const router = new Router();

app.use(bodyParser({
    enableTypes: ['json'],
}));

router.post('/compile', async (ctx) => {
    const { fileName, fileContent } = ctx.request.body;

    if (!fileName || !fileContent) {
        ctx.status = 400;
        ctx.body = { hasError: true, compilerError: 'fileName and fileContent are required.' };
        return;
    }

    const extension = fileName.split('.').pop();
    let command;
    let compilerError = null;

    if (extension === 'ts') {
        // Write TypeScript content to a temporary file
        const tsFilePath = '/tmp/' + fileName;
        await new Promise((resolve, reject) => {
            exec(`echo "${fileContent}" > ${tsFilePath}`, (error) => {
                if (error) {
                    reject(error);
                } else {
                    resolve();
                }
            });
        });

        // Compile TypeScript
        command = `tsc ${tsFilePath} --noEmit`;
    } else if (extension === 'cpp') {
        // Write C++ content to a temporary file
        const cppFilePath = '/tmp/' + fileName;
        await new Promise((resolve, reject) => {
            exec(`echo "${fileContent}" > ${cppFilePath}`, (error) => {
                if (error) {
                    reject(error);
                } else {
                    resolve();
                }
            });
        });

        // Compile C++
        command = `g++ ${cppFilePath} -o /tmp/${fileName}.out`;
    } else {
        ctx.status = 400;
        ctx.body = { hasError: true, compilerError: 'Unsupported file extension. Use .ts or .cpp.' };
        return;
    }

    // Execute the compilation command
    await new Promise((resolve, reject) => {
        exec(command, (error, stdout, stderr) => {
            if (error) {
                compilerError = stderr || 'Compilation failed with an unknown error.';
                reject(compilerError);
            } else {
                resolve();
            }
        });
    }).catch(() => {});

    ctx.body = {
        hasError: !!compilerError,
        compilerError: compilerError || null,
    };
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});