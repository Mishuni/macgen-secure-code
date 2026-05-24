const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const fs = require('fs').promises; // Use promises for async file operations
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const fileType = require('file-type');

// Directory to store uploaded images
const UPLOAD_DIR = path.join(__dirname, 'uploads');

// Ensure the upload directory exists
fs.mkdir(UPLOAD_DIR, { recursive: true }).catch(err => {
  fastify.log.error(err);
});

// Register multipart plugin
fastify.register(multipart);

// Upload endpoint
fastify.post('/upload', async (request, reply) => {
  const data = await request.file();

  // Validate file type (check content)
  const buffer = await data.toBuffer();
  const type = await fileType.fromBuffer(buffer);
  const validMimeTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

  if (!type || !validMimeTypes.includes(type.mime)) {
    return reply.status(400).send({ error: 'Invalid file type. Only images are allowed.' });
  }

  // Sanitize filename and generate a unique ID for the image
  const imageId = uuidv4();
  const ext = path.extname(data.filename).replace(/[^a-z0-9]/gi, ''); // Sanitize extension
  const sanitizedFilename = path.basename(data.filename, ext).replace(/[^a-z0-9]/gi, '') + ext; // Sanitize filename
  const filePath = path.join(UPLOAD_DIR, `${imageId}${sanitizedFilename}`);

  // Check if file already exists (this is now a race condition)
  // Instead, we will directly write and handle the error if it exists
  const writeStream = fs.createWriteStream(filePath);
  data.pipe(writeStream);

  writeStream.on('finish', () => {
    reply.send({ id: imageId });
  });

  writeStream.on('error', (err) => {
    request.log.error(err);
    reply.status(500).send({ error: 'Internal server error' });
  });
});

// Get image endpoint
fastify.get('/images/:imageId', async (request, reply) => {
  const { imageId } = request.params;
  const files = await fs.readdir(UPLOAD_DIR);
  const file = files.find(f => f.startsWith(imageId));

  if (!file) {
    return reply.status(404).send({ error: 'Image not found' });
  }

  const filePath = path.join(UPLOAD_DIR, file);
  reply.type(`image/${path.extname(file).slice(1)}`);
  return reply.sendFile(filePath);
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