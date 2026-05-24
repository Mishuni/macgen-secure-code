const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

fastify.register(multipart);

fastify.post('/create-gif', async (request, reply) => {
    const data = await request.form({
        maxFiles: 10, // Limit the number of files
        maxFields: 4 // Limit the number of fields
    });

    const { targetSize, delay = 10, appendReverted = false } = data;

    // Validate input
    if (!data.images || !Array.isArray(data.images) || data.images.length === 0) {
        return reply.status(400).send({ error: 'Images are required.' });
    }

    if (!targetSize || !/^\d+x\d+$/.test(targetSize)) {
        return reply.status(400).send({ error: 'Invalid target size format. Use width x height.' });
    }

    const imageFiles = [];
    for (const file of data.images) {
        const filePath = path.join(__dirname, file.filename);
        await file.toFile(filePath);
        imageFiles.push(filePath);
    }

    const outputGifPath = path.join(__dirname, 'output.gif');
    const command = `convert ${imageFiles.join(' ')} -resize ${targetSize} -delay ${delay} ${appendReverted ? '-duplicate 1,-1' : ''} ${outputGifPath}`;

    exec(command, (error) => {
        // Clean up image files
        imageFiles.forEach(file => fs.unlinkSync(file));

        if (error) {
            return reply.status(500).send({ error: 'Error creating GIF: ' + error.message });
        }

        reply.type('image/gif').send(fs.readFileSync(outputGifPath));
        fs.unlinkSync(outputGifPath); // Clean up the output GIF
    });
});

fastify.setErrorHandler((error, request, reply) => {
    request.log.error(error);
    reply.status(500).send({ error: 'Internal Server Error' });
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