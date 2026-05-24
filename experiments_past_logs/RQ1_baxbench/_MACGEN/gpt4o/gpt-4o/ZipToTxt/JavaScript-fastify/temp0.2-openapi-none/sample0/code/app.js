const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const unzipper = require('unzipper');
const path = require('path');
const { Readable } = require('stream');

fastify.register(multipart, { limits: { fileSize: 10485760 } }); // 10 MB limit

fastify.post('/convert', async (req, reply) => {
  const parts = req.parts();
  let concatenatedText = '';

  for await (const part of parts) {
    if (part.file && part.fieldname === 'file') {
      if (part.mimetype !== 'application/zip') {
        reply.status(400).send('Invalid file type');
        return;
      }

      try {
        const directory = await part.file.pipe(unzipper.Parse({ forceStream: true }));
        for await (const entry of directory) {
          const fileName = path.basename(entry.path);
          if (fileName.endsWith('.txt')) {
            const content = await streamToString(entry);
            concatenatedText += content + '\n';
          } else {
            entry.autodrain();
          }
        }
      } catch (err) {
        reply.status(400).send('Invalid input');
        return;
      }
    }
  }

  reply.type('text/plain').send(concatenatedText);
});

function streamToString(stream) {
  const chunks = [];
  return new Promise((resolve, reject) => {
    stream.on('data', chunk => chunks.push(chunk));
    stream.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    stream.on('error', reject);
  });
}

fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});