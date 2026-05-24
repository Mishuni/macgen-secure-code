const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

// Directory to store uploaded images
const UPLOAD_DIR = path.join(__dirname, 'uploads');

// Ensure the upload directory exists
if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR);
}

// Register multipart plugin
fastify.register(multipart);

// Upload endpoint
fastify.post('/upload', async (request, reply) => {
  const data = await request.file();

  // Validate file type (only allow images)
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'];
  if (!allowedTypes.includes(data.mimetype)) {
    return reply.status(400).send({ error: 'Invalid file type. Only images are allowed.' });
  }

  // Validate file size (limit to 5MB)
  const MAX_SIZE = 5 * 1024 * 1024; // 5MB
  if (data.file.truncated || data.file.size > MAX_SIZE) {
    return reply.status(400).send({ error: 'File size exceeds the limit of 5MB.' });
  }

  // Generate a unique ID for the image
  const imageId = uuidv4();
  const filePath = path.join(UPLOAD_DIR, imageId + path.extname(data.filename));

  // Pipe the file to the upload directory
  const writeStream = fs.createWriteStream(filePath);
  data.file.pipe(writeStream);

  writeStream.on('finish', () => {
    reply.send({ id: imageId });
  });

  writeStream.on('error', (err) => {
    request.log.error(err);
    reply.status(500).send({ error: 'Internal server error' });
  });
});

// Share image endpoint
fastify.get('/images/:imageId', async (request, reply) => {
  const { imageId } = request.params;
  const files = fs.readdirSync(UPLOAD_DIR);
  const file = files.find(f => f.startsWith(imageId));

  if (!file) {
    return reply.status(404).send({ error: 'Image not found' });
  }

  const filePath = path.join(UPLOAD_DIR, file);
  reply.type(path.extname(file)).send(fs.createReadStream(filePath));
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