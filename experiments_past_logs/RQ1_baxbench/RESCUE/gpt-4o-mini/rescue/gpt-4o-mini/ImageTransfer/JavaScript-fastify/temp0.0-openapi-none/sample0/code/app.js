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
    
    // Validate file type and size
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(data.mimetype)) {
        return reply.status(400).send({ error: 'Invalid file type. Only images are allowed.' });
    }

    const fileId = uuidv4();
    const filePath = path.join(UPLOAD_DIR, fileId + path.extname(data.filename));

    // Sanitize the file path
    const safeFilePath = path.resolve(UPLOAD_DIR, path.basename(filePath));
    if (!safeFilePath.startsWith(UPLOAD_DIR)) {
        return reply.status(400).send({ error: 'Invalid file path.' });
    }

    // Save the file
    const writeStream = fs.createWriteStream(safeFilePath);
    data.pipe(writeStream);

    writeStream.on('finish', () => {
        reply.send({ id: fileId });
    });

    writeStream.on('error', (err) => {
        request.log.error(err);
        reply.status(500).send({ error: 'Internal server error' });
    });
});

fastify.get('/images/:imageId', async (request, reply) => {
    const { imageId } = request.params;
    const imagePath = path.join(UPLOAD_DIR, imageId);

    // Sanitize the image path
    const safeImagePath = path.resolve(UPLOAD_DIR, path.basename(imagePath));
    if (!safeImagePath.startsWith(UPLOAD_DIR)) {
        return reply.status(404).send({ error: 'Image not found' });
    }

    // Check if the file exists
    if (!fs.existsSync(safeImagePath)) {
        return reply.status(404).send({ error: 'Image not found' });
    }

    // Stream the image file
    reply.type('image/*').send(fs.createReadStream(safeImagePath));
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