const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const MAX_FILES = 10; // Limit the number of files
const ALLOWED_EXTENSIONS = ['.pdf']; // Allowed file extensions

fastify.register(multipart);

fastify.post('/concatenate', async (request, reply) => {
    const data = await request.form({ maxFiles: MAX_FILES });
    const files = data.files;

    // Validate that files are present
    if (!files || files.length === 0) {
        return reply.status(400).send({ error: 'Invalid input or missing files.' });
    }

    // Validate file extensions
    for (const file of files) {
        const ext = path.extname(file.filename);
        if (!ALLOWED_EXTENSIONS.includes(ext)) {
            return reply.status(400).send({ error: 'Invalid file type. Only PDF files are allowed.' });
        }
    }

    const tempFiles = [];
    try {
        // Save uploaded files to temporary location
        for (const file of files) {
            const tempPath = path.join(__dirname, file.filename);
            await file.toFile(tempPath);
            tempFiles.push(tempPath);
        }

        const outputFilePath = path.join(__dirname, 'concatenated.pdf');
        const command = `pdfunite ${tempFiles.join(' ')} ${outputFilePath}`;

        // Execute the pdfunite command
        await new Promise((resolve, reject) => {
            exec(command, (error) => {
                if (error) {
                    return reject(error);
                }
                resolve();
            });
        });

        // Send the concatenated PDF file as response
        reply.type('application/pdf').send(fs.createReadStream(outputFilePath));
    } catch (error) {
        return reply.status(500).send({ error: 'An error occurred while processing the files.' });
    } finally {
        // Clean up temporary files
        for (const tempFile of tempFiles) {
            fs.unlink(tempFile, (err) => {
                if (err) {
                    fastify.log.error(`Failed to delete temp file: ${tempFile}`);
                }
            });
        }
    }
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