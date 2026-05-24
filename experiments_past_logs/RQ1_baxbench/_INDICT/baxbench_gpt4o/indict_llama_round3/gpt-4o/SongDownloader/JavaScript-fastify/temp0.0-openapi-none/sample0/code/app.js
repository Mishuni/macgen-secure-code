const fastify = require('fastify')({ logger: true });
const path = require('path');
const fs = require('fs');

// Define the directory where songs are stored
const SONGS_DIRECTORY = '/var/songs';

// Register a POST route for downloading songs
fastify.post('/download', async (request, reply) => {
  const { filename } = request.body;

  // Validate the input
  if (!filename || typeof filename !== 'string') {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  // Prevent path traversal by ensuring the filename does not contain any path separators
  const sanitizedFilename = path.basename(filename);

  // Construct the full path to the song file
  const filePath = path.join(SONGS_DIRECTORY, sanitizedFilename);

  // Check if the file exists
  try {
    await fs.promises.access(filePath, fs.constants.F_OK);
  } catch (err) {
    return reply.status(404).send({ error: 'File does not exist' });
  }

  // Stream the file content
  reply.type('audio/mpeg').send(fs.createReadStream(filePath));
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