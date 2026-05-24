const fastify = require('fastify')({ logger: true });
const path = require('path');
const fs = require('fs');
const mime = require('mime-types');

// Define the directory where songs are stored
const SONGS_DIR = '/var/songs';

// Helper function to validate the filename
function isValidFilename(filename) {
  // Ensure the filename is a string and does not contain directory traversal characters
  return typeof filename === 'string' && !filename.includes('..') && path.basename(filename) === filename;
}

// Define the route for downloading songs
fastify.post('/download', async (request, reply) => {
  try {
    // Validate Content-Type header
    const contentType = request.headers['content-type'];
    if (!contentType || !contentType.includes('application/json')) {
      return reply.status(400).send({ error: 'Invalid Content-Type' });
    }

    // Parse and validate the request body
    const { filename } = request.body;
    if (!isValidFilename(filename)) {
      return reply.status(400).send({ error: 'Invalid filename' });
    }

    // Construct the full path to the song file
    const filePath = path.join(SONGS_DIR, filename);
    const realPath = fs.realpathSync(filePath);

    // Ensure the file is within the SONGS_DIR
    if (!realPath.startsWith(SONGS_DIR)) {
      return reply.status(400).send({ error: 'Invalid file path' });
    }

    // Check if the file exists and stream it
    fs.access(realPath, fs.constants.R_OK, (err) => {
      if (err) {
        return reply.status(404).send({ error: 'File does not exist' });
      }

      // Stream the file
      const mimeType = mime.lookup(realPath) || 'audio/mpeg';
      reply.type(mimeType);
      const stream = fs.createReadStream(realPath);
      stream.pipe(reply.raw);
    });
  } catch (error) {
    // Handle errors gracefully
    fastify.log.error(error);
    reply.status(500).send({ error: 'Internal Server Error' });
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