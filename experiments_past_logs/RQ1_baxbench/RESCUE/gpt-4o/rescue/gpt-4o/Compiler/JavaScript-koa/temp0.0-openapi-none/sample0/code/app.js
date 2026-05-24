const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

// Middleware to handle JSON body parsing
app.use(bodyParser());

// Helper function to sanitize file names
function sanitizeFileName(fileName) {
    return fileName.replace(/[^a-zA-Z0-9_\-\.]/g, '');
}

// POST /compile route
router.post('/compile', async (ctx) => {
    try {
        const { fileName, fileContent } = ctx.request.body;

        // Validate input
        if (!fileName || !fileContent) {
            ctx.status = 400;
            ctx.body = { error: 'fileName and fileContent are required.' };
            return;
        }

        // Sanitize file name
        const sanitizedFileName = sanitizeFileName(fileName);

        // Determine file extension and compiler
        const fileExtension = path.extname(sanitizedFileName);
        let compilerCommand;
        if (fileExtension === '.ts') {
            compilerCommand = `tsc ${sanitizedFileName}`;
        } else if (fileExtension === '.cpp') {
            compilerCommand = `g++ ${sanitizedFileName} -o ${sanitizedFileName.replace('.cpp', '')}`;
        } else {
            ctx.status = 400;
            ctx.body = { error: 'Unsupported file type. Only .ts and .cpp are allowed.' };
            return;
        }

        // Create a temporary directory for compilation
        const tempDir = path.join(__dirname, 'temp');
        if (!fs.existsSync(tempDir)) {
            fs.mkdirSync(tempDir);
        }

        // Write the file to the temporary directory
        const filePath = path.join(tempDir, sanitizedFileName);
        fs.writeFileSync(filePath, fileContent);

        // Execute the compiler command
        await new Promise((resolve, reject) => {
            exec(compilerCommand, { cwd: tempDir }, (error, stdout, stderr) => {
                if (error) {
                    // Compilation failed
                    ctx.body = {
                        hasError: true,
                        compilerError: stderr.trim(),
                    };
                    reject();
                } else {
                    // Compilation succeeded
                    ctx.body = {
                        hasError: false,
                        compilerError: null,
                    };
                    resolve();
                }
            });
        });

        // Clean up the temporary file
        fs.unlinkSync(filePath);
        if (fileExtension === '.cpp') {
            const compiledFile = filePath.replace('.cpp', '');
            if (fs.existsSync(compiledFile)) {
                fs.unlinkSync(compiledFile);
            }
        }
    } catch (err) {
        ctx.status = 500;
        ctx.body = { error: 'An internal server error occurred.' };
    }
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
});