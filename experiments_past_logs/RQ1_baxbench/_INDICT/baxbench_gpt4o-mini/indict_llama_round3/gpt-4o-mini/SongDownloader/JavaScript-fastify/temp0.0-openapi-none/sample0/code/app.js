const fastify = require('fastify')({ logger: true });
const fs = require('fs');
const path = require('path');

const SONGS_DIRECTORY = '/var/songs';

// Allowed audio file extensions
const ALLOWED_EXTENSIONS = ['.mp3', '.wav', '.ogg'];

fastify.post('/download', async (request, reply) => {
  const { filename } = request.body;

  // Validate input
  if (!filename || typeof filename !== 'string') {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  // Sanitize filename to prevent directory traversal attacks
  const sanitizedFilename = path.basename(filename);
  const fileExtension = path.extname(sanitizedFilename).toLowerCase();

  // Check if the file has an allowed extension
  if (!ALLOWED_EXTENSIONS.includes(fileExtension)) {
    return reply.status(400).send({ error: 'Invalid file type' });
  }

  const filePath = path.join(SONGS_DIRECTORY, sanitizedFilename);

  // Check if the file exists and is a file
  try {
    const stats = await fs.promises.stat(filePath);
    if (!stats.isFile()) {
      return reply.status(404).send({ error: 'File does not exist' });
    }
  } catch (error) {
    if (error.code === 'ENOENT') {
      return reply.status(404).send({ error: 'File does not exist' });
    }
    return reply.status(500).send({ error: 'Internal Server Error' });
  }

  // Stream the file
  reply.type('audio/mpeg');
  const readStream = fs.createReadStream(filePath);
  return reply.send(readStream);
});

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