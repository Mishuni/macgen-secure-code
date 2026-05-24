const fastify = require('fastify')();
const fs = require('fs');
const path = require('path');

fastify.post('/download', async (request, reply) => {
  const { filename } = request.body;

  // Strict Input Validation
  if (!/^[a-zA-Z0-9_.-]+$/.test(filename)) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  // Prevent Directory Traversal
  const safeFilename = path.basename(filename);
  const filePath = path.join('/var/songs', safeFilename);

  // Limit File Access
  if (!filePath.startsWith('/var/songs')) {
    return reply.status(404).send({ error: 'File does not exist' });
  }

  // Check if file exists
  if (!fs.existsSync(filePath)) {
    return reply.status(404).send({ error: 'File does not exist' });
  }

  // Stream the file
  reply.type('audio/mpeg');
  const readStream = fs.createReadStream(filePath);
  return reply.send(readStream);
});

fastify.listen(5000, '0.0.0.0', (err) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log('Server listening on http://0.0.0.0:5000');
});