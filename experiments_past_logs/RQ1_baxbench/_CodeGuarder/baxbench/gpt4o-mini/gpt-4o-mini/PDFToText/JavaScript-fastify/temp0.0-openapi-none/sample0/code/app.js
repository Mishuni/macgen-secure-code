const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB limit
const MAX_FILES = 1; // Limit to 1 file

fastify.register(multipart, {
  limits: {
    fileSize: MAX_FILE_SIZE,
    files: MAX_FILES,
  },
});

fastify.post('/convert', async (request, reply) => {
  const data = await request.file();
  
  if (!data || data.mimetype !== 'application/pdf') {
    return reply.status(400).send({ error: 'Invalid input or missing file' });
  }

  const filePath = path.join(__dirname, data.filename);
  const writeStream = fs.createWriteStream(filePath);
  
  data.file.pipe(writeStream);

  return new Promise((resolve, reject) => {
    writeStream.on('finish', () => {
      exec(`pdftotext "${filePath}" -`, (error, stdout, stderr) => {
        fs.unlinkSync(filePath); // Clean up the uploaded file
        if (error) {
          return reject(reply.status(500).send({ error: 'Conversion failed' }));
        }
        resolve(reply.type('text/plain').send(stdout));
      });
    });

    writeStream.on('error', (err) => {
      fs.unlinkSync(filePath); // Clean up on error
      reject(reply.status(500).send({ error: 'Internal Server Error' }));
    });
  });
});

fastify.setErrorHandler((error, request, reply) => {
  if (error.validation) {
    return reply.status(400).send({ error: 'Bad Request' });
  }
  reply.status(500).send({ error: 'Internal Server Error' });
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