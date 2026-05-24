const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const unzipper = require('unzipper');
const path = require('path');
const { pipeline } = require('stream');
const { promisify } = require('util');
const pump = promisify(pipeline);

fastify.register(multipart, {
  limits: {
    fileSize: 10 * 1024 * 1024, // Limit file size to 10MB
    files: 1, // Only one file per request
  },
});

fastify.post('/convert', async (request, reply) => {
  const parts = request.parts();
  let filePart;

  for await (const part of parts) {
    if (part.file && part.fieldname === 'file') {
      filePart = part;
      break;
    }
  }

  if (!filePart) {
    return reply.status(400).send('Invalid input: No file uploaded');
  }

  try {
    const textContents = [];
    const directory = filePart.file.pipe(unzipper.Parse({ forceStream: true }));

    for await (const entry of directory) {
      const fileName = entry.path;
      const fileType = entry.type; // 'Directory' or 'File'

      if (fileType === 'File' && path.extname(fileName) === '.txt') {
        const chunks = [];
        for await (const chunk of entry) {
          chunks.push(chunk);
        }
        textContents.push(Buffer.concat(chunks).toString('utf8'));
      } else {
        entry.autodrain();
      }
    }

    const resultText = textContents.join('\n');
    reply.type('text/plain').send(resultText);
  } catch (error) {
    request.log.error(error);
    reply.status(400).send('Error processing zip file');
  }
});

fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});