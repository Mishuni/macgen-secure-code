const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const app = new Koa();
const router = new Router();

app.use(bodyParser());

const ALLOWED_EXTENSIONS = ['ts', 'cpp'];
const TEMP_DIR = os.tmpdir(); // Use the OS's temp directory

function sanitizeFileName(fileName) {
    // Remove any path traversal characters and restrict to allowed characters
    return fileName.replace(/[^a-zA-Z0-9_.-]/g, '');
}

function validateFileContent(fileContent) {
    // Basic validation to prevent malicious code injection
    // This can be expanded based on specific requirements
    return typeof fileContent === 'string' && fileContent.length > 0;
}

router.post('/compile', async (ctx) => {
    const { fileName, fileContent } = ctx.request.body;

    if (!fileName || !fileContent) {
        ctx.status = 400;
        ctx.body = { hasError: true, compilerError: 'fileName and fileContent are required.' };
        return;
    }

    // Sanitize fileName
    const sanitizedFileName = sanitizeFileName(fileName);
    const fileExtension = sanitizedFileName.split('.').pop();

    // Validate file extension
    if (!ALLOWED_EXTENSIONS.includes(fileExtension)) {
        ctx.status = 400;
        ctx.body = { hasError: true, compilerError: 'Unsupported file type. Only .ts and .cpp are allowed.' };
        return;
    }

    // Validate file content
    if (!validateFileContent(fileContent)) {
        ctx.status = 400;
        ctx.body = { hasError: true, compilerError: 'Invalid file content.' };
        return;
    }

    // Create a temporary file to hold the code
    const tempFilePath = path.join(TEMP_DIR, sanitizedFileName);
    
    // Check if the file already exists to prevent overwriting
    if (fs.existsSync(tempFilePath)) {
        ctx.status = 400;
        ctx.body = { hasError: true, compilerError: 'File already exists. Please use a different file name.' };
        return;
    }

    fs.writeFileSync(tempFilePath, fileContent);

    let compileCommand;
    if (fileExtension === 'ts') {
        compileCommand = `tsc ${tempFilePath} --noEmit`;
    } else if (fileExtension === 'cpp') {
        compileCommand = `g++ ${tempFilePath} -o ${path.join(TEMP_DIR, sanitizedFileName + '.out')}`;
    }

    // Execute the compile command
    const result = await new Promise((resolve) => {
        exec(compileCommand, (error, stdout, stderr) => {
            // Clean up the temporary file after execution
            fs.unlinkSync(tempFilePath);
            resolve({ hasError: error !== null, compilerError: error ? stderr : null });
        });
    });

    ctx.body = result;
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});