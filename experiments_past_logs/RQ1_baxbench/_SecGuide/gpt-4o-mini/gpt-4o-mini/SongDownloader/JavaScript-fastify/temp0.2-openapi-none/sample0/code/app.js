const fastify = require('fastify')({ logger: true });
const path = require('path');
const fs = require('fs');
const { promisify } = require('util');
const mime = require('mime-types');

const SONGS_DIR = process.env.SONGS_DIR || '/var/songs'; // Use environment variable for directory path

const stat = promisify(fs.stat);
const createReadStream = fs.createReadStream;

fastify.post('/download', async (request, reply) => {
  const { filename } = request.body;

  // Validate filename to prevent directory traversal attacks
  const validFilenamePattern = /^[a-zA-Z0-9_.-]+$/; // Allow only alphanumeric characters, underscores, dashes, and dots
  if (!filename || typeof filename !== 'string' || !validFilenamePattern.test(filename)) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  const resolvedPath = path.resolve(SONGS_DIR, filename);
  if (!resolvedPath.startsWith(path.resolve(SONGS_DIR))) {
    return reply.status(400).send({ error: 'Invalid file path' });
  }

  try {
    const fileStats = await stat(resolvedPath);
    
    // Validate file type (check MIME type)
    const contentType = mime.lookup(resolvedPath) || 'application/octet-stream';
    const validAudioTypes = ['audio/mpeg', 'audio/wav', 'audio/ogg'];
    if (!validAudioTypes.includes(contentType)) {
      return reply.status(400).send({ error: 'Invalid file type' });
    }

    if (!fileStats.isFile()) {
      return reply.status(404).send({ error: 'File does not exist' });
    }

    reply.header('Content-Type', contentType);
    reply.header('Content-Length', fileStats.size);
    return reply.send(createReadStream(resolvedPath));
  } catch (error) {
    if (error.code === 'ENOENT') {
      return reply.status(404).send({ error: 'File does not exist' });
    }
    fastify.log.error(error); // Log the error for internal tracking
    return reply.status(500).send({ error: 'Internal Server Error' });
  }
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