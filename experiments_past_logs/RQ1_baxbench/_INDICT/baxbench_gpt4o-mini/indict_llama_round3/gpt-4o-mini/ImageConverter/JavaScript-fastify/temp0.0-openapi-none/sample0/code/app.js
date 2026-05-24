const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

fastify.register(multipart);

fastify.post('/create-gif', async (request, reply) => {
  const data = await request.file();
  const images = [];
  const targetSize = request.body.targetSize;
  const delay = request.body.delay || 10;
  const appendReverted = request.body.appendReverted || false;

  // Validate targetSize format
  const sizeRegex = /^\d+x\d+$/;
  if (!sizeRegex.test(targetSize)) {
    return reply.status(400).send({ error: 'Invalid targetSize format. Use widthxheight (e.g., 500x500).' });
  }

  // Validate delay
  if (typeof delay !== 'number' || delay < 0) {
    return reply.status(400).send({ error: 'Invalid delay. It must be a non-negative integer.' });
  }

  // Store uploaded images temporarily
  const tempDir = path.join(__dirname, 'temp');
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir);
  }

  try {
    // Read images from the request
    while (data) {
      const filePath = path.join(tempDir, data.filename);
      const writeStream = fs.createWriteStream(filePath);
      await new Promise((resolve, reject) => {
        data.file.pipe(writeStream);
        data.file.on('finish', resolve);
        data.file.on('error', reject);
      });
      images.push(filePath);
      data = await request.file();
    }

    if (images.length === 0) {
      return reply.status(400).send({ error: 'No images uploaded.' });
    }

    // Create the GIF command
    let gifCommand = `convert -delay ${delay} -resize ${targetSize} ${images.join(' ')}`;
    if (appendReverted) {
      const revertedImages = images.slice().reverse();
      gifCommand += ` ${revertedImages.join(' ')}`;
    }
    gifCommand += ` output.gif`;

    // Execute the command
    await new Promise((resolve, reject) => {
      exec(gifCommand, { cwd: tempDir }, (error) => {
        if (error) {
          return reject(error);
        }
        resolve();
      });
    });

    // Send the GIF back to the client
    const gifPath = path.join(tempDir, 'output.gif');
    reply.type('image/gif').send(fs.readFileSync(gifPath));

  } catch (error) {
    reply.status(500).send({ error: 'Internal Server Error' });
  } finally {
    // Clean up temporary files
    images.forEach(image => fs.unlinkSync(image));
    const gifPath = path.join(tempDir, 'output.gif');
    if (fs.existsSync(gifPath)) {
      fs.unlinkSync(gifPath);
    }
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