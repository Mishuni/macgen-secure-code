import fastify from 'fastify';
import fastifyMultipart from '@fastify/multipart';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs';
import path from 'path';
import mime from 'mime-types';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const server = fastify();
const uploadDir = path.join(__dirname, 'uploads');

// Ensure the upload directory exists
if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir);
}

// Register the multipart plugin
server.register(fastifyMultipart, {
    limits: {
        fileSize: 5 * 1024 * 1024, // Limit file size to 5MB
    }
});

// Helper function to validate imageId
const isValidImageId = (imageId) => /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/.test(imageId);

// Route to handle image uploads
server.post('/upload', async (request, reply) => {
    const data = await request.file();
    if (!data) {
        return reply.status(400).send({ error: 'No file uploaded' });
    }

    // Validate file type
    const allowedMimeTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!allowedMimeTypes.includes(data.mimetype)) {
        return reply.status(400).send({ error: 'Invalid file type' });
    }

    const fileId = uuidv4();
    const filePath = path.join(uploadDir, fileId);

    // Save the file to the uploads directory
    try {
        await new Promise((resolve, reject) => {
            const writeStream = fs.createWriteStream(filePath);
            data.file.pipe(writeStream);
            data.file.on('end', resolve);
            data.file.on('error', reject);
        });
    } catch (error) {
        console.error('Error saving file:', error);
        return reply.status(500).send({ error: 'Internal server error' });
    }

    return reply.send({ id: fileId });
});

// Route to serve uploaded images
server.get('/images/:imageId', async (request, reply) => {
    const { imageId } = request.params;

    if (!isValidImageId(imageId)) {
        return reply.status(400).send({ error: 'Invalid image ID' });
    }

    const filePath = path.join(uploadDir, imageId);

    if (!fs.existsSync(filePath)) {
        return reply.status(404).send({ error: 'Image not found' });
    }

    // Validate the file's MIME type by inspecting its content
    const mimeType = mime.lookup(filePath);
    if (!mimeType || !['image/jpeg', 'image/png', 'image/gif'].includes(mimeType)) {
        return reply.status(400).send({ error: 'Invalid file type' });
    }

    // Stream the image file to the client
    return reply.type(mimeType).send(fs.createReadStream(filePath));
});

// Start the server
server.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
    if (err) {
        console.error(err);
        process.exit(1);
    }
    console.log(`Server listening at ${address}`);
});