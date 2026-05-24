const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

fastify.register(multipart);

fastify.post('/concatenate', async (request, reply) => {
    const data = await request.file();
    const files = [];

    // Collect all uploaded files
    while (data) {
        const filePath = path.join(__dirname, data.filename);
        const writeStream = fs.createWriteStream(filePath);
        data.file.pipe(writeStream);

        await new Promise((resolve, reject) => {
            writeStream.on('finish', () => {
                files.push(filePath);
                resolve();
            });
            writeStream.on('error', reject);
        });

        data = await request.file();
    }

    if (files.length === 0) {
        return reply.status(400).send({ error: 'Invalid input or missing files.' });
    }

    const outputFilePath = path.join(__dirname, 'concatenated.pdf');

    // Construct the command to concatenate PDFs
    const command = `pdfunite ${files.join(' ')} ${outputFilePath}`;

    return new Promise((resolve, reject) => {
        exec(command, (error) => {
            if (error) {
                return reject(reply.status(500).send({ error: 'An error occurred while processing the files.' }));
            }

            // Read the concatenated PDF and send it as a response
            reply.type('application/pdf').send(fs.createReadStream(outputFilePath));

            // Clean up temporary files
            files.forEach(file => fs.unlinkSync(file));
            fs.unlinkSync(outputFilePath);
        });
    });
});

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