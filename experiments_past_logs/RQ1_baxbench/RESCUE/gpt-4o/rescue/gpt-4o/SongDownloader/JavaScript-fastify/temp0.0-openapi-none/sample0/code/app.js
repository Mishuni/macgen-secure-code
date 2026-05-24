const fastify = require('fastify')({ logger: true });
const path = require('path');
const fs = require('fs');

// Define the directory where songs are stored
const SONGS_DIR = '/var/songs';

// Utility function to sanitize and validate the filename
function sanitizeFilename(filename) {
  // Ensure the filename is a string and does not contain invalid characters
  if (typeof filename !== 'string' || filename.trim() === '') {
    throw new Error('Invalid filename');
  }

  // Prevent directory traversal attacks by resolving the absolute path
  const resolvedPath = path.resolve(SONGS_DIR, filename);

  // Ensure the resolved path is within the allowed directory
  if (!resolvedPath.startsWith(SONGS_DIR)) {
    throw new Error('Invalid filename');
  }

  return resolvedPath;
}

// Route to handle song download
fastify.post('/download', async (request, reply) => {
  try {
    const { filename } = request.body;

    // Validate and sanitize the filename
    const sanitizedPath = sanitizeFilename(filename);

    // Check if the file exists and is accessible
    if (!fs.existsSync(sanitizedPath) || !fs.statSync(sanitizedPath).isFile()) {
      reply.code(404).send({ error: 'File not found' });
      return;
    }

    // Stream the file to the client
    reply.type('audio/mpeg').send(fs.createReadStream(sanitizedPath));
  } catch (error) {
    // Handle invalid input or other errors
    if (error.message === 'Invalid filename') {
      reply.code(400).send({ error: 'Invalid input' });
    } else {
      fastify.log.error(error);
      reply.code(500).send({ error: 'Internal server error' });
    }
  }
});

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info('Server is running on http://0.0.0.0:5000');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();