const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

// Register multipart plugin
fastify.register(multipart);

// Route to concatenate PDF files
fastify.post('/concatenate', async (request, reply) => {
  const parts = request.parts();
  const files = [];
  const tempDir = path.join(__dirname, 'temp', uuidv4());

  // Create a unique temporary directory for this request
  fs.mkdirSync(tempDir, { recursive: true });

  try {
    for await (const part of parts) {
      if (part.file && part.fieldname === 'files') {
        const sanitizedFilename = path.basename(part.filename).replace(/[^a-zA-Z0-9.\-_]/g, '');
        const filePath = path.join(tempDir, sanitizedFilename);
        const writeStream = fs.createWriteStream(filePath);
        await part.pipe(writeStream);
        files.push(filePath);
      }
    }

    if (files.length < 2) {
      return reply.status(400).send({ error: 'Invalid input or missing files.' });
    }

    const outputFilePath = path.join(tempDir, 'concatenated.pdf');
    const command = `pdfunite ${files.map(file => `"${file}"`).join(' ')} "${outputFilePath}"`;

    exec(command, (error) => {
      if (error) {
        return reply.status(500).send({ error: 'An error occurred while processing the files.' });
      }

      reply.type('application/pdf').send(fs.createReadStream(outputFilePath));

      // Clean up the temporary directory after sending
      fs.rmSync(tempDir, { recursive: true, force: true });
    });
  } catch (err) {
    // Clean up in case of error
    fs.rmSync(tempDir, { recursive: true, force: true });
    reply.status(500).send({ error: 'An error occurred while processing the files.' });
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