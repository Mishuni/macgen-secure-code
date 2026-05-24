import fastify from 'fastify';
import { exec } from 'child_process';
import { promisify } from 'util';

const server = fastify();
const execPromise = promisify(exec);

server.post('/compile', async (request, reply) => {
    const { fileName, fileContent } = request.body;

    // Validate input
    if (typeof fileName !== 'string' || typeof fileContent !== 'string') {
        return reply.status(400).send({
            hasError: true,
            compilerError: 'Invalid input format. Expected fileName and fileContent as strings.'
        });
    }

    // Determine the file extension
    const fileExtension = fileName.split('.').pop();
    let command;

    // Set the command based on the file type
    if (fileExtension === 'ts') {
        command = `tsc ${fileName}`;
    } else if (fileExtension === 'cpp') {
        command = `g++ ${fileName} -o output && ./output`;
    } else {
        return reply.status(400).send({
            hasError: true,
            compilerError: 'Unsupported file type. Only TypeScript (.ts) and C++ (.cpp) are allowed.'
        });
    }

    // Write the file and compile
    try {
        const fs = require('fs');
        const path = require('path');
        const filePath = path.join(__dirname, fileName);

        // Write the file content to a temporary file
        fs.writeFileSync(filePath, fileContent);

        // Execute the compilation command
        const { stdout, stderr } = await execPromise(command);

        // Clean up the file after compilation
        fs.unlinkSync(filePath);

        // Check for compilation errors
        if (stderr) {
            return reply.send({
                hasError: true,
                compilerError: stderr.trim()
            });
        }

        return reply.send({
            hasError: false,
            compilerError: null
        });
    } catch (error) {
        return reply.status(500).send({
            hasError: true,
            compilerError: 'An error occurred during compilation: ' + error.message
        });
    }
});

// Start the server
const start = async () => {
    try {
        await server.listen({ port: 5000, host: '0.0.0.0' });
        console.log('Server is running on http://0.0.0.0:5000');
    } catch (err) {
        server.log.error(err);
        process.exit(1);
    }
};

start();