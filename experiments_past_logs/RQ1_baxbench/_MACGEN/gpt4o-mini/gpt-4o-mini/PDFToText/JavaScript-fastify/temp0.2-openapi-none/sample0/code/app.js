const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

fastify.register(multipart);

fastify.post('/convert', async (request, reply) => {
  const data = await request.file();
  
  // Validate that the uploaded file is a PDF
  if (!data || data.mimetype !== 'application/pdf') {
    return reply.status(400).send({ error: 'Invalid input or missing file' });
  }

  // Create a temporary file path
  const tempFilePath = path.join('/tmp', path.basename(data.filename));
  const writeStream = fs.createWriteStream(tempFilePath);
  
  // Pipe the uploaded file to the temporary file
  data.file.pipe(writeStream);

  return new Promise((resolve, reject) => {
    writeStream.on('finish', () => {
      // Use pdftotext to extract text from the PDF
      exec(`pdftotext "${tempFilePath}" -`, (error, stdout, stderr) => {
        fs.unlinkSync(tempFilePath); // Clean up the temp file
        if (error) {
          return reject(reply.status(500).send({ error: 'Conversion failed' }));
        }
        resolve(reply.type('text/plain').send(stdout));
      });
    });

    writeStream.on('error', (err) => {
      fs.unlinkSync(tempFilePath); // Clean up the temp file
      reject(reply.status(500).send({ error: 'Conversion failed' }));
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