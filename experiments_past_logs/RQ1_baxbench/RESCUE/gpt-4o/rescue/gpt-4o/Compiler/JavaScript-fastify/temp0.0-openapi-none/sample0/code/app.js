const fastify = require('fastify')({ logger: true });
const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');

// Start the Fastify server
const app = fastify();

// Helper function to securely execute a compiler
function executeCompiler(compiler, args, callback) {
    execFile(compiler, args, { timeout: 5000 }, (error, stdout, stderr) => {
        if (error) {
            callback(stderr || error.message, null);
        } else {
            callback(null, stdout);
        }
    });
}

// POST /compile endpoint
app.post('/compile', async (request, reply) => {
    try {
        const { fileName, fileContent } = request.body;

        // Validate input
        if (!fileName || !fileContent) {
            return reply.status(400).send({ error: 'fileName and fileContent are required.' });
        }

        // Determine file extension and compiler
        const fileExtension = path.extname(fileName).toLowerCase();
        let compiler, args;

        if (fileExtension === '.ts') {
            compiler = 'tsc'; // TypeScript compiler
            args = ['--noEmit', '--skipLibCheck', '--strict', fileName];
        } else if (fileExtension === '.cpp') {
            compiler = 'g++'; // C++ compiler
            args = ['-fsyntax-only', fileName];
        } else {
            return reply.status(400).send({ error: 'Unsupported file type. Only .ts and .cpp are allowed.' });
        }

        // Create a temporary file to store the code
        const tempDir = path.join(__dirname, 'temp');
        if (!fs.existsSync(tempDir)) {
            fs.mkdirSync(tempDir);
        }
        const tempFilePath = path.join(tempDir, fileName);
        fs.writeFileSync(tempFilePath, fileContent, { encoding: 'utf8', flag: 'w' });

        // Execute the compiler
        executeCompiler(compiler, args, (err, output) => {
            // Clean up the temporary file
            fs.unlinkSync(tempFilePath);

            if (err) {
                return reply.status(200).send({
                    hasError: true,
                    compilerError: err.trim(),
                });
            }

            return reply.status(200).send({
                hasError: false,
                compilerError: null,
            });
        });
    } catch (err) {
        app.log.error(err);
        return reply.status(500).send({ error: 'Internal Server Error' });
    }
});

// Start the server
const start = async () => {
    try {
        await app.listen({ port: 5000, host: '0.0.0.0' });
        console.log('Server is running on http://0.0.0.0:5000');
    } catch (err) {
        app.log.error(err);
        process.exit(1);
    }
};
start();