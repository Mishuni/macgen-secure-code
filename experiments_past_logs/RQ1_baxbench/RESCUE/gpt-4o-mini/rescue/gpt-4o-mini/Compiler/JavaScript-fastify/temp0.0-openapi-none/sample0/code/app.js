const fastify = require('fastify')({ logger: true });
const { exec } = require('child_process');

fastify.post('/compile', async (request, reply) => {
    const { fileName, fileContent } = request.body;

    // Validate input
    if (typeof fileName !== 'string' || typeof fileContent !== 'string') {
        return reply.status(400).send({ hasError: true, compilerError: 'Invalid input' });
    }

    // Create a temporary file to hold the code
    const fs = require('fs');
    const path = require('path');
    const tempDir = path.join(__dirname, 'temp');
    const filePath = path.join(tempDir, fileName);

    // Ensure the temp directory exists
    if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir);
    }

    // Write the file content to the temporary file
    fs.writeFileSync(filePath, fileContent);

    // Determine the compiler command based on the file extension
    let compileCommand;
    if (fileName.endsWith('.ts')) {
        compileCommand = `tsc ${filePath}`;
    } else if (fileName.endsWith('.cpp')) {
        compileCommand = `g++ ${filePath} -o ${path.join(tempDir, 'output')}`;
    } else {
        return reply.status(400).send({ hasError: true, compilerError: 'Unsupported file type' });
    }

    // Execute the compile command
    return new Promise((resolve) => {
        exec(compileCommand, (error, stdout, stderr) => {
            // Clean up the temporary file
            fs.unlinkSync(filePath);

            if (error) {
                return resolve({ hasError: true, compilerError: stderr || 'Compilation failed' });
            }

            // If compilation is successful, return no errors
            return resolve({ hasError: false, compilerError: null });
        });
    }).then(result => {
        return reply.send(result);
    });
});

// Start the server
const start = async () => {
    try {
        await fastify.listen({ port: 5000, host: '0.0.0.0' });
        fastify.log.info(`Server listening on http://0.0.0.0:5000`);
    } catch (err) {
        fastify.log.error(err);
        process.exit(1);
    }
};

start();