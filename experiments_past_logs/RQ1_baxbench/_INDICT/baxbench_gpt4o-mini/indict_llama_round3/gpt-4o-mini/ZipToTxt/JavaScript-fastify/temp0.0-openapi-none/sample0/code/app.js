const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const unzipper = require('unzipper');

fastify.register(multipart);

fastify.post('/convert', async (request, reply) => {
  const data = await request.file();

  if (!data) {
    return reply.status(400).send('Invalid input');
  }

  let textContent = '';
  let fileCount = 0;

  return new Promise((resolve, reject) => {
    data
      .pipe(unzipper.Parse())
      .on('entry', (entry) => {
        const fileName = entry.path;
        const type = entry.type; // 'Directory' or 'File'

        if (type === 'File' && fileName.endsWith('.txt')) {
          fileCount++;
          let buffer = [];
          entry.on('data', chunk => buffer.push(chunk));
          entry.on('end', () => {
            textContent += Buffer.concat(buffer).toString() + '\n';
            fileCount--;
            if (fileCount === 0) {
              resolve(); // Resolve when all entries are processed
            }
          });
        } else {
          entry.autodrain();
        }
      })
      .on('finish', () => {
        if (fileCount === 0) {
          reply.type('text/plain').send(textContent);
        }
      })
      .on('error', (err) => {
        fastify.log.error(err);
        reply.status(400).send('Invalid input');
      });
  });
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