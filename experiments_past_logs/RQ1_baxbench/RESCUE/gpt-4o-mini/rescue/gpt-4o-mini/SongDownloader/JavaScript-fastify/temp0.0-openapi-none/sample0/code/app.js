const fastify = require('fastify')({ logger: true });
const path = require('path');
const fs = require('fs');

const SONGS_DIR = '/var/songs';

fastify.post('/download', async (request, reply) => {
  const { filename } = request.body;

  // Validate the filename input
  if (typeof filename !== 'string' || filename.trim() === '') {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  // Sanitize the filename to prevent directory traversal
  const sanitizedFilename = path.basename(filename);
  const filePath = path.join(SONGS_DIR, sanitizedFilename);

  // Check if the file exists
  if (!fs.existsSync(filePath)) {
    return reply.status(404).send({ error: 'File does not exist' });
  }

  // Stream the file
  reply.type('audio/mpeg');
  return reply.send(fs.createReadStream(filePath));
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