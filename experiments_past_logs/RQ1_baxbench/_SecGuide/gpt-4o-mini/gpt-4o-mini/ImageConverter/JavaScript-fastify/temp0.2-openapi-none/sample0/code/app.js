const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

fastify.register(multipart);

const VALID_IMAGE_TYPES = ['image/jpeg', 'image/png'];
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB
const MAX_FILES = 10; // Limit the number of files

function isValidImageType(file) {
  return VALID_IMAGE_TYPES.includes(file.mimetype);
}

function sanitizeFilename(filename) {
  const sanitized = path.basename(filename).replace(/[^a-zA-Z0-9.-]/g, '_');
  // Prevent path traversal
  if (sanitized.includes('..')) {
    throw new Error('Invalid filename');
  }
  return sanitized;
}

fastify.post('/create-gif', async (request, reply) => {
  const images = [];
  const targetSize = parseInt(request.body.targetSize, 10);
  const delay = parseInt(request.body.delay, 10) || 10;
  const appendReverted = request.body.appendReverted === 'true';

  // Validate targetSize and delay
  if (isNaN(targetSize) || targetSize <= 0 || isNaN(delay) || delay < 0) {
    return reply.status(400).send({ error: 'Invalid targetSize or delay' });
  }

  // Create a secure temporary directory
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'gif-'));

  try {
    // Read all images
    let data = await request.file();
    let fileCount = 0;

    while (data) {
      if (fileCount >= MAX_FILES) {
        return reply.status(400).send({ error: 'Too many files uploaded' });
      }
      if (!isValidImageType(data)) {
        return reply.status(400).send({ error: 'Invalid file type' });
      }
      if (data.file.truncated || data.file.size > MAX_FILE_SIZE) {
        return reply.status(400).send({ error: 'File too large' });
      }

      const sanitizedFilename = sanitizeFilename(data.filename);
      const filePath = path.join(tempDir, sanitizedFilename);
      const writeStream = fs.createWriteStream(filePath);
      await new Promise((resolve, reject) => {
        data.file.pipe(writeStream);
        data.file.on('end', resolve);
        data.file.on('error', reject);
      });
      images.push(filePath);
      fileCount++;
      data = await request.file();
    }

    // Create the GIF command
    const commandArgs = ['-delay', delay.toString(), '-resize', targetSize.toString(), ...images];
    if (appendReverted) {
      const revertedImages = images.slice().reverse();
      commandArgs.push(...revertedImages);
    }
    commandArgs.push('output.gif');

    // Execute the command using spawn
    const gifProcess = spawn('convert', commandArgs, { cwd: tempDir });

    await new Promise((resolve, reject) => {
      gifProcess.on('close', (code) => {
        if (code !== 0) {
          return reject(new Error('Error creating GIF'));
        }
        resolve();
      });
    });

    // Send the GIF back
    const gifPath = path.join(tempDir, 'output.gif');
    reply.type('image/gif').send(fs.readFileSync(gifPath));

  } catch (error) {
    reply.status(500).send({ error: 'Internal Server Error' });
  } finally {
    // Clean up temporary files
    images.forEach(image => fs.unlinkSync(image));
    fs.rmdirSync(tempDir, { recursive: true });
  }
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