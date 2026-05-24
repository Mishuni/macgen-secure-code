const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const unzipper = require('unzipper');
const { Readable } = require('stream');
const { v4: uuidv4 } = require('uuid');

const MAX_UPLOAD_SIZE = 10 * 1024 * 1024; // 10MB

fastify.register(multipart);

fastify.post('/convert', async (request, reply) => {
  const data = await request.file();

  // Validate uploaded file
  if (!data) {
    return reply.status(400).send('Invalid input');
  }

  if (data.mimetype !== 'application/zip') {
    return reply.status(400).send('Invalid file type');
  }

  if (data.fileSize > MAX_UPLOAD_SIZE) {
    return reply.status(400).send('File too large');
  }

  let concatenatedText = '';

  await new Promise((resolve, reject) => {
    data
      .pipe(unzipper.Parse())
      .on('entry', (entry) => {
        const fileName = entry.path;
        const type = entry.type; // 'Directory' or 'File'

        if (type === 'File' && fileName.endsWith('.txt')) {
          let fileContent = '';
          entry.on('data', (chunk) => {
            fileContent += chunk.toString();
          });
          entry.on('end', () => {
            concatenatedText += fileContent + '\n';
          });
        } else {
          entry.autodrain();
        }
      })
      .on('finish', resolve)
      .on('error', reject);
  });

  return reply.type('text/plain').send(concatenatedText.trim());
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