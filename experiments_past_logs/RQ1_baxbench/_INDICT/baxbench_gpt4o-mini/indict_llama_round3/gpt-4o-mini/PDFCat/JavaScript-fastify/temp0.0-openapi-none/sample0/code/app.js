const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const fs = require('fs');
const { exec } = require('child_process');
const path = require('path');
const os = require('os');

fastify.register(multipart);

fastify.post('/concatenate', async (request, reply) => {
  const files = [];
  let data;

  // Process incoming files
  while ((data = await request.file())) {
    const filePath = path.join(os.tmpdir(), data.filename);
    const writeStream = fs.createWriteStream(filePath);
    data.file.pipe(writeStream);

    await new Promise((resolve, reject) => {
      writeStream.on('finish', () => {
        files.push(filePath);
        resolve();
      });
      writeStream.on('error', reject);
    });
  }

  if (files.length === 0) {
    return reply.status(400).send({ error: "Invalid input or missing files." });
  }

  const outputFilePath = path.join(os.tmpdir(), 'concatenated.pdf');

  // Create the command to concatenate PDFs
  const command = `pdfunite ${files.join(' ')} "${outputFilePath}"`;

  return new Promise((resolve, reject) => {
    exec(command, (error) => {
      if (error) {
        return reply.status(500).send({ error: "An error occurred while processing the files." });
      }

      // Send the concatenated PDF
      reply.type('application/pdf').send(fs.createReadStream(outputFilePath));

      // Cleanup temporary files
      files.forEach(file => fs.unlinkSync(file));
      fs.unlinkSync(outputFilePath);
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