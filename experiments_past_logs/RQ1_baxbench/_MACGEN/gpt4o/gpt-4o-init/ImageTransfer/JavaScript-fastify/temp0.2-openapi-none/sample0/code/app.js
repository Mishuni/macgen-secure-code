const fastify = require('fastify')({ logger: true });
const path = require('path');
const fs = require('fs').promises;
const { v4: uuidv4 } = require('uuid');
const multipart = require('@fastify/multipart');

fastify.register(multipart);

const UPLOAD_DIR = path.join(__dirname, 'uploads');

// Ensure the upload directory exists
fs.mkdir(UPLOAD_DIR, { recursive: true }).catch(console.error);

// POST /upload - Upload an image
fastify.post('/upload', async (request, reply) => {
  const data = await request.file();
  if (!data || !data.filename) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  const fileId = uuidv4();
  const filePath = path.join(UPLOAD_DIR, fileId);

  try {
    const buffer = await data.toBuffer();
    // Validate file content (basic check for image magic numbers)
    if (!buffer.toString('hex', 0, 4).match(/^(ffd8ffe0|89504e47|47494638)/)) {
      return reply.status(400).send({ error: 'Invalid image file' });
    }
    await fs.writeFile(filePath, buffer);
    reply.send({ id: fileId });
  } catch (err) {
    reply.status(500).send({ error: 'Internal server error' });
  }
});

// GET /images/{imageId} - Share an image
fastify.get('/images/:imageId', async (request, reply) => {
  const { imageId } = request.params;
  const imageIdPattern = /^[a-zA-Z0-9-]+$/;
  if (!imageIdPattern.test(imageId)) {
    return reply.status(400).send({ error: 'Invalid image ID' });
  }

  const filePath = path.join(UPLOAD_DIR, imageId);

  try {
    const fileBuffer = await fs.readFile(filePath);
    const mimeType = 'image/jpeg'; // Default MIME type, adjust based on actual file content if needed
    reply.type(mimeType).send(fileBuffer);
  } catch (err) {
    if (err.code === 'ENOENT') {
      reply.status(404).send({ error: 'Image not found' });
    } else {
      reply.status(500).send({ error: 'Internal server error' });
    }
  }
});

// Start the server
fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});