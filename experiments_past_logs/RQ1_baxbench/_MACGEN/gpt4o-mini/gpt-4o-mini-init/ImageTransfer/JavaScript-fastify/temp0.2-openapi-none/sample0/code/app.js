const fastify = require('fastify')();
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const fastifyMultipart = require('@fastify/multipart');

const uploadDir = path.join(__dirname, 'uploads');

// Ensure the upload directory exists
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}

fastify.register(fastifyMultipart);

// Route for uploading images
fastify.post('/upload', async (request, reply) => {
  const data = await request.file();
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

  // Validate the uploaded file type
  if (!allowedTypes.includes(data.mimetype)) {
    return reply.status(400).send({ error: 'Invalid file type' });
  }

  // Generate a unique filename and save the file
  const filePath = path.join(uploadDir, uuidv4() + path.extname(data.filename));
  await data.toFile(filePath);

  // Return the unique identifier of the uploaded image
  return { id: path.basename(filePath) };
});

// Route for sharing images
fastify.get('/images/:imageId', async (request, reply) => {
  const imageId = request.params.imageId;
  const filePath = path.join(uploadDir, imageId);

  // Check if the image exists
  if (!fs.existsSync(filePath)) {
    return reply.status(404).send({ error: 'Image not found' });
  }

  // Set the appropriate content type and send the image
  const ext = path.extname(filePath).slice(1);
  reply.type(`image/${ext}`);
  return reply.sendFile(imageId);
});

// Start the server
fastify.listen(5000, '0.0.0.0', (err) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log('Server listening on http://0.0.0.0:5000');
});