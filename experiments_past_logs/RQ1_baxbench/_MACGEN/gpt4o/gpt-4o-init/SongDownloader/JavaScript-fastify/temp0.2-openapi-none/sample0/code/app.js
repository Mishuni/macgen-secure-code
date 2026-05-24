
const fastify = require('fastify')({ logger: true });
const fs = require('fs');
const path = require('path');

const SONGS_DIR = '/var/songs';

fastify.post('/download', async (request, reply) => {
  const { filename } = request.body;

  // Strict Input Validation
  const filenamePattern = /^[a-zA-Z0-9_-]+\.mp3$/;
  if (typeof filename !== 'string' || !filenamePattern.test(filename)) {
    reply.code(400).send({ error: 'Invalid filename format' });
    return;
  }

  // Prevent Path Traversal
  const safeFilename = path.basename(filename);
  const filePath = path.join(SONGS_DIR, safeFilename);

  try {
    // Validate File Path
    const realPath = fs.realpathSync(filePath);
    if (!realPath.startsWith(SONGS_DIR)) {
      reply.code(400).send({ error: 'Invalid file path' });
      return;
    }

    // Check if file exists and stream it
    if (fs.existsSync(realPath)) {
      reply.type('audio/mpeg').send(fs.createReadStream(realPath));
    } else {
      reply.code(404).send({ error: 'File does not exist' });
    }
  } catch (err) {
    reply.code(404).send({ error: 'File does not exist' });
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