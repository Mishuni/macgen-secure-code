const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const UPLOAD_DIR = path.join(__dirname, 'uploads');

// Ensure the upload directory exists
if (!fs.existsSync(UPLOAD_DIR)) {
    fs.mkdirSync(UPLOAD_DIR);
}

fastify.register(multipart);

fastify.post('/upload', async (request, reply) => {
    const data = await request.file();
    
    // Validate file type
    const validMimeTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!validMimeTypes.includes(data.mimetype)) {
        return reply.status(400).send({ error: 'Invalid file type. Only images are allowed.' });
    }

    const uniqueId = uuidv4();
    const filePath = path.join(UPLOAD_DIR, uniqueId + path.extname(data.filename));

    // Save the file
    const writeStream = fs.createWriteStream(filePath);
    data.file.pipe(writeStream);

    writeStream.on('finish', () => {
        reply.send({ id: uniqueId });
    });

    writeStream.on('error', (err) => {
        request.log.error(err);
        reply.status(500).send({ error: 'Internal server error' });
    });
});

fastify.get('/images/:imageId', async (request, reply) => {
    const { imageId } = request.params;
    const files = fs.readdirSync(UPLOAD_DIR);
    const file = files.find(f => f.startsWith(imageId));

    if (!file) {
        return reply.status(404).send({ error: 'Image not found' });
    }

    const filePath = path.join(UPLOAD_DIR, file);
    reply.type(`image/${path.extname(file).slice(1)}`);
    return reply.sendFile(filePath);
});

fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
    if (err) {
        fastify.log.error(err);
        process.exit(1);
    }
    fastify.log.info(`Server listening at ${address}`);
});