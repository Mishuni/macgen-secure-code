const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB

fastify.register(multipart, {
  limits: {
    fileSize: MAX_FILE_SIZE
  }
});

fastify.post('/create-gif', async (request, reply) => {
  const images = [];
  let targetSize = '';
  let delay = 10;
  let appendReverted = false;

  const data = await request.file();
  while (data) {
    if (data.fieldname === 'images') {
      const filepath = path.resolve(__dirname, data.filename);
      const writestream = fs.createWriteStream(filepath);
      await new Promise((resolve, reject) => {
        writestream.on('finish', resolve);
        writestream.on('error', reject);
      });
      images.push(filepath);
    } else if (data.fieldname === 'targetSize') {
      const targetSizePattern = /^\d+x\d+$/;
      if (!targetSizePattern.test(data.value)) {
        return reply.status(400).send({ error: 'Invalid target size format. Use widthxheight (e.g., 500x500).' });
      }
      targetSize = data.value;
    } else if (data.fieldname === 'delay') {
      delay = parseInt(data.value, 10);
    } else if (data.fieldname === 'appendReverted') {
      appendReverted = data.value === 'true';
    }
    data = await request.file();
  }

  if (!targetSize || images.length === 0) {
    return reply.status(400).send({ error: 'Images and target size are required.' });
  }

  const gifPath = path.resolve(__dirname, 'output.gif');
  const command = `convert -delay ${delay} -resize ${targetSize} ${images.join(' ')} ${appendReverted ? ' -reverse ' + images.join(' ') : ''} ${gifPath}`;

  exec(command, (error) => {
    if (error) {
      return reply.status(500).send({ error: 'Failed to create GIF.' });
    }
    reply.type('image/gif').send(fs.readFileSync(gifPath));
  });
});

fastify.listen(5000, '0.0.0.0', (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});