const fastify = require('fastify')({ logger: true });
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const fastifyMultipart = require('@fastify/multipart');

// Initialize Fastify server
fastify.register(fastifyMultipart, {
  limits: {
    fileSize: 10 * 1024 * 1024, // 10 MB
    files: 1, // Only one file per request
  },
});

// Store uploaded images in memory for simplicity
const images = new Map();

// Define the /upload route
fastify.post('/upload', async (request, reply) => {
  const data = await request.file();
  if (!data) {
    return reply.status(400).send({ error: 'No file uploaded' });
  }

  const fileId = uuidv4();
  const filePath = path.join(__dirname, 'uploads', fileId);

  // Validate file type (basic check)
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
  if (!allowedTypes.includes(data.mimetype)) {
    return reply.status(400).send({ error: 'Invalid file type' });
  }

  // Store the file
  await new Promise((resolve, reject) => {
    const fileStream = fs.createWriteStream(filePath);
    data.file.pipe(fileStream);
    data.file.on('end', resolve);
    data.file.on('error', reject);
  });

  images.set(fileId, { path: filePath, mimetype: data.mimetype });

  return reply.send({ id: fileId });
});

// Define the /images/{imageId} route
fastify.get('/images/:imageId', async (request, reply) => {
  const { imageId } = request.params;
  const image = images.get(imageId);

  if (!image) {
    return reply.status(404).send({ error: 'Image not found' });
  }

  return reply.type(image.mimetype).send(fs.createReadStream(image.path));
});

// Handle error responses
fastify.setErrorHandler((error, request, reply) => {
  request.log.error(error);
  reply.status(500).send({ error: 'Internal server error' });
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