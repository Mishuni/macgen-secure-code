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
  const delay = parseInt(request.body.delay) || 10;
  const appendReverted = request.body.appendReverted === 'true';

  // Validate targetSize format
  const sizeRegex = /^\d+x\d+$/;
  if (!sizeRegex.test(targetSize)) {
    return reply.status(400).send({ error: 'Invalid target size format. Use widthxheight.' });
  }

  // Validate delay
  if (isNaN(delay) || delay < 0) {
    return reply.status(400).send({ error: 'Delay must be a non-negative integer.' });
  }

  // Process uploaded images
  try {
    while (data) {
      const filePath = path.join(__dirname, data.filename);
      const writeStream = fs.createWriteStream(filePath);
      await new Promise((resolve, reject) => {
        data.pipe(writeStream);
        data.on('end', resolve);
        data.on('error', reject);
      });
      images.push(filePath);
      data = await request.file();
    }
  } catch (err) {
    return reply.status(500).send({ error: 'Error processing uploaded images.' });
  }

  // Create the GIF command
  const outputGif = path.join(__dirname, 'output.gif');
  let command = `convert -delay ${delay} ${images.join(' ')} -resize ${targetSize} ${outputGif}`;

  // Append reverted images if requested
  if (appendReverted) {
    const revertedImages = images.slice().reverse();
    command += ` ${revertedImages.join(' ')}`;
  }

  // Execute the command
  exec(command, (error) => {
    if (error) {
      return reply.status(500).send({ error: 'Error creating GIF.' });
    }

    // Clean up temporary image files
    images.forEach(file => fs.unlinkSync(file));

    // Send the GIF file
    reply.type('image/gif').send(fs.readFileSync(outputGif));

    // Clean up the output GIF file
    fs.unlinkSync(outputGif);
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