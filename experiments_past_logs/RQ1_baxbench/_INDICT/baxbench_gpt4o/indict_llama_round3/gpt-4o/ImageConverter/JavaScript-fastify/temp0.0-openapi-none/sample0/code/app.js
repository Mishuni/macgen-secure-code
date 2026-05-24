const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

fastify.register(multipart);

fastify.post('/create-gif', async (req, reply) => {
  const parts = req.parts();
  const imageFiles = [];
  let targetSize, delay = 10, appendReverted = false;

  try {
    for await (const part of parts) {
      if (part.file) {
        const filePath = path.join(__dirname, 'uploads', `${uuidv4()}-${path.basename(part.filename)}`);
        await part.toFile(filePath);
        imageFiles.push(filePath);
      } else {
        if (part.fieldname === 'targetSize') {
          if (!/^\d+x\d+$/.test(part.value)) {
            return reply.status(400).send({ error: 'Invalid targetSize format. Expected format: WIDTHxHEIGHT' });
          }
          targetSize = part.value;
        } else if (part.fieldname === 'delay') {
          delay = parseInt(part.value, 10);
          if (isNaN(delay) || delay < 0) {
            return reply.status(400).send({ error: 'Invalid delay value. Must be a non-negative integer.' });
          }
        } else if (part.fieldname === 'appendReverted') {
          appendReverted = part.value === 'true';
        }
      }
    }

    if (!imageFiles.length || !targetSize) {
      return reply.status(400).send({ error: 'images and targetSize are required fields' });
    }

    const gifPath = path.join(__dirname, 'uploads', `${uuidv4()}.gif`);
    let commandArgs = ['-delay', delay.toString(), '-resize', targetSize, ...imageFiles];

    if (appendReverted) {
      commandArgs.push(...imageFiles.slice().reverse());
    }

    commandArgs.push(gifPath);

    execFile('convert', commandArgs, (error) => {
      if (error) {
        return reply.status(500).send({ error: 'Failed to create GIF' });
      }

      reply.type('image/gif').send(fs.createReadStream(gifPath));

      // Clean up temporary files
      imageFiles.forEach(file => fs.unlinkSync(file));
      fs.unlinkSync(gifPath);
    });
  } catch (err) {
    return reply.status(500).send({ error: 'Internal Server Error' });
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