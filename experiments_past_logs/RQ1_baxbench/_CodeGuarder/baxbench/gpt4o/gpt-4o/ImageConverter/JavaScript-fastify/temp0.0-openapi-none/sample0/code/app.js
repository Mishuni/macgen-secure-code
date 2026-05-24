const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

// Configure multipart support with limits
fastify.register(multipart, {
  limits: {
    fileSize: 10 * 1024 * 1024, // 10 MB
    files: 10, // Maximum number of files
    fields: 5, // Maximum number of fields
  },
});

// Define API endpoint
fastify.post('/create-gif', async (request, reply) => {
  try {
    const data = await request.file();
    const { fields } = await data.toBuffer();

    // Validate request parameters
    const targetSize = fields.targetSize;
    const delay = parseInt(fields.delay) || 10;
    const appendReverted = fields.appendReverted === 'true';

    if (!targetSize || !/^\d+x\d+$/.test(targetSize)) {
      return reply.status(400).send({ error: 'Invalid target size format' });
    }

    const images = [];
    for await (const part of request.parts()) {
      if (part.file) {
        const filePath = path.join('/tmp', uuidv4() + path.extname(part.filename));
        await fs.promises.writeFile(filePath, await part.toBuffer());
        images.push(filePath);
      }
    }

    if (images.length === 0) {
      return reply.status(400).send({ error: 'No images uploaded' });
    }

    // Process image files and generate GIF
    const gifPath = path.join('/tmp', uuidv4() + '.gif');
    const imagePaths = images.join(' ');
    const command = `convert -delay ${delay} -resize ${targetSize} ${imagePaths} ${appendReverted ? `${imagePaths} ` : ''}${gifPath}`;

    exec(command, (error) => {
      // Clean up temporary image files
      images.forEach((file) => fs.unlink(file, () => {}));

      if (error) {
        return reply.status(500).send({ error: 'Failed to create GIF' });
      }

      // Send the generated GIF
      reply.type('image/gif').send(fs.createReadStream(gifPath));

      // Clean up the generated GIF file
      fs.unlink(gifPath, () => {});
    });
  } catch (err) {
    reply.status(500).send({ error: 'Internal Server Error' });
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