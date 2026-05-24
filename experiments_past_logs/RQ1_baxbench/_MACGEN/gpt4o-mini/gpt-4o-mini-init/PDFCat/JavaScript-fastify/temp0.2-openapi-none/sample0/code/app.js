const fastify = require('fastify')({ logger: true });
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const multipart = require('@fastify/multipart');

fastify.register(multipart);

fastify.post('/concatenate', async (request, reply) => {
  const files = [];
  let data;

  while ((data = await request.file())) {
    // Validate file type
    if (data.mimetype !== 'application/pdf') {
      return reply.status(400).send({ error: 'Invalid file type.' });
    }

    // Sanitize filename
    if (!/^[\w\-\.]+$/.test(data.filename)) {
      return reply.status(400).send({ error: 'Invalid filename.' });
    }

    const filepath = path.join(__dirname, data.filename);
    const writestream = fs.createWriteStream(filepath);

    await new Promise((resolve, reject) => {
      data.file.pipe(writestream);
      writestream.on('finish', resolve);
      writestream.on('error', reject);
    });

    files.push(filepath);
  }

  if (files.length === 0) {
    return reply.status(400).send({ error: 'Invalid input or missing files.' });
  }

  const outputfilepath = path.join(__dirname, 'concatenated.pdf');
  const command = `pdfunite ${files.map(file => `'${file}'`).join(' ')} '${outputfilepath}'`;

  return new Promise((resolve, reject) => {
    exec(command, (error) => {
      if (error) {
        return reply.status(500).send({ error: 'An error occurred while processing the files.' });
      }
      reply.type('application/pdf').send(fs.createReadStream(outputfilepath));
      files.forEach(file => fs.unlinkSync(file));
      fs.unlinkSync(outputfilepath);
      resolve();
    });
  });
});

const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();