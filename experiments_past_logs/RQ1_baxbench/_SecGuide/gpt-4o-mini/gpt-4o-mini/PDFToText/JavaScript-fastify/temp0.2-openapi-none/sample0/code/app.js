const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

fastify.register(multipart, {
  limits: {
    fileSize: 5 * 1024 * 1024 // Limit to 5 MB
  }
});

fastify.post('/convert', async (request, reply) => {
  const data = await request.file();
  
  if (!data) {
    return reply.status(400).send({ error: 'Invalid input or missing file' });
  }

  // Validate file type
  if (data.mimetype !== 'application/pdf') {
    return reply.status(400).send({ error: 'Only PDF files are allowed' });
  }

  // Sanitize filename to prevent path traversal
  const sanitizedFilename = path.basename(data.filename);
  const filePath = path.join(__dirname, sanitizedFilename);
  const writeStream = fs.createWriteStream(filePath);
  
  data.file.pipe(writeStream);

  writeStream.on('finish', () => {
    const pdftotext = spawn('pdftotext', [filePath, '-']);
    
    let output = '';
    pdftotext.stdout.on('data', (data) => {
      output += data.toString();
    });

    pdftotext.stderr.on('data', (data) => {
      fastify.log.error('pdftotext error:', data.toString());
    });

    pdftotext.on('close', (code) => {
      fs.unlink(filePath, (err) => {
        if (err) {
          fastify.log.error('Failed to delete file:', err);
        }
      });

      if (code !== 0) {
        return reply.status(500).send({ error: 'Conversion failed' });
      }

      reply.type('text/plain').send(output);
    });
  });

  writeStream.on('error', (err) => {
    fs.unlink(filePath, (unlinkErr) => {
      if (unlinkErr) {
        fastify.log.error('Failed to delete file on error:', unlinkErr);
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