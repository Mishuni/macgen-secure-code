const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');

// Register multipart plugin
fastify.register(multipart);

// Define the /concatenate route
fastify.post('/concatenate', async (request, reply) => {
  const parts = request.parts();
  const files = [];
  const tempDir = fs.mkdtempSync('/tmp/pdf-concat-');

  try {
    for await (const part of parts) {
      if (part.file && part.fieldname === 'files') {
        const filePath = path.join(tempDir, part.filename);
        const writeStream = fs.createWriteStream(filePath);
        await part.file.pipe(writeStream);
        files.push(filePath);
      }
    }

    if (files.length === 0) {
      return reply.status(400).send({ error: 'Invalid input or missing files.' });
    }

    const outputFilePath = path.join(tempDir, 'concatenated.pdf');
    const command = ['pdfunite', ...files, outputFilePath];

    execFile(command[0], command.slice(1), (error) => {
      if (error) {
        return reply.status(500).send({ error: 'An error occurred while processing the files.' });
      }

      reply.type('application/pdf').send(fs.createReadStream(outputFilePath));
    });
  } catch (err) {
    reply.status(500).send({ error: 'An error occurred while processing the files.' });
  } finally {
    // Clean up temporary files
    files.forEach(file => fs.unlinkSync(file));
    fs.rmdirSync(tempDir, { recursive: true });
  }
});

// Start the server
fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});