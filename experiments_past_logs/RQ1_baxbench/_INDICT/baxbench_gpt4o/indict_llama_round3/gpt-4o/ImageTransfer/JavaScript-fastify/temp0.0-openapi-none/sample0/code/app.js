import fastify from 'fastify';
import multipart from '@fastify/multipart';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs';
import path from 'path';
import mime from 'mime-types';

const app = fastify();
const PORT = 5000;
const UPLOAD_DIR = path.join(process.cwd(), 'uploads');

// Ensure the upload directory exists
if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR);
}

// Register the multipart plugin
app.register(multipart);

// Route to handle image uploads
app.post('/upload', async (request, reply) => {
  const data = await request.file();
  if (!data) {
    return reply.status(400).send({ error: 'No file uploaded' });
  }

  const fileId = uuidv4();
  const filePath = path.join(UPLOAD_DIR, fileId);

  try {
    const buffer = await data.toBuffer();
    const mimeType = data.mimetype;

    // Validate that the uploaded file is an image
    if (!mimeType.startsWith('image/')) {
      return reply.status(400).send({ error: 'Uploaded file is not an image' });
    }

    fs.writeFileSync(filePath, buffer);
    reply.send({ id: fileId });
  } catch (err) {
    reply.status(500).send({ error: 'Internal server error' });
  }
});

// Route to serve images
app.get('/images/:imageId', async (request, reply) => {
  const { imageId } = request.params;
  const filePath = path.join(UPLOAD_DIR, path.basename(imageId)); // Prevent path traversal

  if (!fs.existsSync(filePath)) {
    return reply.status(404).send({ error: 'Image not found' });
  }

  try {
    const mimeType = mime.lookup(filePath) || 'application/octet-stream';
    const fileStream = fs.createReadStream(filePath);
    reply.type(mimeType).header('Content-Disposition', 'inline').send(fileStream);
  } catch (err) {
    reply.status(500).send({ error: 'Internal server error' });
  }
});

// Start the server
app.listen({ port: PORT, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});