import fastify from 'fastify';
import multipart from '@fastify/multipart';
import { v4 as uuidv4 } from 'uuid';
import path from 'path';
import fs from 'fs/promises';

const app = fastify();
const PORT = 5000;
const HOST = '0.0.0.0';

// Directory to store uploaded images
const STORAGE_DIR = path.resolve('./uploads');

// Ensure the storage directory exists
async function ensureStorageDir() {
    try {
        await fs.mkdir(STORAGE_DIR, { recursive: true });
    } catch (err) {
        console.error('Error creating storage directory:', err);
        process.exit(1);
    }
}

// Middleware for handling multipart form data
app.register(multipart);

// Route to upload an image
app.post('/upload', async (req, reply) => {
    try {
        const data = await req.file();

        // Validate file presence
        if (!data || !data.filename) {
            return reply.status(400).send({ error: 'No file uploaded' });
        }

        // Generate a unique ID for the image
        const imageId = uuidv4();
        const fileExtension = path.extname(data.filename);
        const safeFileName = `${imageId}${fileExtension}`;
        const filePath = path.join(STORAGE_DIR, safeFileName);

        // Validate file type (basic validation for images)
        const allowedMimeTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        if (!allowedMimeTypes.includes(data.mimetype)) {
            return reply.status(400).send({ error: 'Unsupported file type' });
        }

        // Save the file securely
        await fs.writeFile(filePath, await data.toBuffer());

        // Return the shareable link
        return reply.status(200).send({ id: imageId });
    } catch (err) {
        console.error('Error during file upload:', err);
        return reply.status(500).send({ error: 'Internal server error' });
    }
});

// Route to view an image
app.get('/images/:imageId', async (req, reply) => {
    try {
        const { imageId } = req.params;

        // Validate imageId
        if (!imageId || typeof imageId !== 'string') {
            return reply.status(400).send({ error: 'Invalid image ID' });
        }

        // Locate the file
        const files = await fs.readdir(STORAGE_DIR);
        const matchingFile = files.find(file => file.startsWith(imageId));

        if (!matchingFile) {
            return reply.status(404).send({ error: 'Image not found' });
        }

        const filePath = path.join(STORAGE_DIR, matchingFile);

        // Stream the file to the client
        return reply.type(`image/${path.extname(matchingFile).slice(1)}`).send(fs.createReadStream(filePath));
    } catch (err) {
        console.error('Error during image retrieval:', err);
        return reply.status(500).send({ error: 'Internal server error' });
    }
});

// Start the server
(async () => {
    await ensureStorageDir();
    try {
        await app.listen({ port: PORT, host: HOST });
        console.log(`Server running at http://${HOST}:${PORT}/`);
    } catch (err) {
        console.error('Error starting server:', err);
        process.exit(1);
    }
})();