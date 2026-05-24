const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const unzipper = require('unzipper');
const { pipeline } = require('stream/promises');
const { StringDecoder } = require('string_decoder');
const path = require('path');
const fs = require('fs');

fastify.register(multipart, {
  limits: {
    fileSize: 10 * 1024 * 1024, // Limit file size to 10MB
    files: 1, // Limit to one file per request
  },
});

fastify.post('/convert', async (req, reply) => {
  const parts = req.parts();
  let textContent = '';

  for await (const part of parts) {
    if (part.file && part.fieldname === 'file') {
      try {
        await pipeline(
          part.file.pipe(unzipper.Parse()),
          async function (source) {
            for await (const entry of source) {
              const fileName = path.basename(entry.path); // Use basename to prevent path traversal
              const decoder = new StringDecoder('utf8');

              if (entry.type === 'File' && fileName.endsWith('.txt')) {
                let fileContent = '';
                for await (const chunk of entry) {
                  fileContent += decoder.write(chunk);
                }
                textContent += fileContent + '\n';
              } else {
                entry.autodrain();
              }
            }
          }
        );
      } catch (err) {
        req.log.error({ err }, 'Error processing file');
        return reply.status(400).send('Invalid input: ' + err.message);
      }
    } else {
      return reply.status(400).send('Invalid input: No file uploaded');
    }
  }

  reply.type('text/plain').send(textContent.trim());
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