const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

fastify.register(multipart);

fastify.post('/convert', async (request, reply) => {
  const data = await request.file();

  if (!data) {
    return reply.status(400).send({ error: 'Invalid input or missing file' });
  }

  const filePath = path.join(__dirname, data.filename);
  const writeStream = fs.createWriteStream(filePath);

  data.file.pipe(writeStream);

  writeStream.on('finish', () => {
    exec(`pdftotext "${filePath}" -`, (error, stdout, stderr) => {
      fs.unlink(filePath, (err) => {
        if (err) {
          fastify.log.error('Error cleaning up file:', err);
        }
      });

      if (error) {
        return reply.status(500).send({ error: 'Conversion failed' });
      }

      reply.type('text/plain').send(stdout);
    });
  });

  writeStream.on('error', (err) => {
    fs.unlink(filePath, (unlinkErr) => {
      if (unlinkErr) {
        fastify.log.error('Error cleaning up file on write error:', unlinkErr);
      }
    });
    return reply.status(500).send({ error: 'Internal Server Error' });
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