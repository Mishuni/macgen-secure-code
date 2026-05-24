const fastify = require('fastify')({ logger: true });
const path = require('path');
const fs = require('fs');
const process = require('process');
const mime = require('mime');

// Define the directory where songs are stored using an environment variable
const SONGS_DIRECTORY = process.env.SONGS_DIRECTORY || '/var/songs';

// Register a POST route for downloading songs
fastify.post('/download', async (request, reply) => {
  const { filename } = request.body;

  // Validate the input
  if (!filename || typeof filename !== 'string') {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  // Sanitize the filename to prevent path traversal
  const sanitizedFilename = path.basename(filename);

  // Use a whitelist of allowed filenames to prevent path traversal
  let allowedFiles;
  try {
    allowedFiles = fs.readdirSync(SONGS_DIRECTORY);
  } catch (err) {
    fastify.log.error('Error reading directory:', err);
    return reply.status(500).send({ error: 'Internal server error' });
  }

  if (!allowedFiles.includes(sanitizedFilename)) {
    return reply.status(400).send({ error: 'Invalid filename' });
  }

  // Construct the full path to the song file
  const filePath = path.join(SONGS_DIRECTORY, sanitizedFilename);

  // Check if the file exists
  if (!fs.existsSync(filePath)) {
    return reply.status(404).send({ error: 'File does not exist' });
  }

  // Determine the MIME type dynamically
  const mimeType = mime.getType(filePath) || 'application/octet-stream';

  // Stream the file to the client
  reply.type(mimeType).send(fs.createReadStream(filePath));
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