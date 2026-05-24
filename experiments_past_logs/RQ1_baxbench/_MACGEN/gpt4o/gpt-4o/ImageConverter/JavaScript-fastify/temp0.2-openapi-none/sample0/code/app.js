const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const util = require('util');
const execPromise = util.promisify(exec);

fastify.register(multipart);

fastify.post('/create-gif', async (request, reply) => {
  try {
    const data = await request.file();
    const fields = await data.fields();
    const images = [];
    let targetSize = fields.targetSize.value;
    let delay = fields.delay ? parseInt(fields.delay.value) : 10;
    let appendReverted = fields.appendReverted ? fields.appendReverted.value === 'true' : false;

    if (!targetSize || !/^\d+x\d+$/.test(targetSize)) {
      return reply.status(400).send({ error: 'Invalid targetSize format. Expected format: WIDTHxHEIGHT' });
    }

    for await (const part of data) {
      if (part.fieldname === 'images') {
        const filePath = path.join(os.tmpdir(), part.filename);
        await part.toFile(filePath);
        images.push(filePath);
      }
    }

    if (images.length === 0) {
      return reply.status(400).send({ error: 'No images provided.' });
    }

    const outputGif = path.join(os.tmpdir(), 'output.gif');
    let convertCommand = `convert ${images.map(img => `"${img}"`).join(' ')} -resize ${targetSize} -delay ${delay} -loop 0 "${outputGif}"`;

    if (appendReverted) {
      convertCommand = `convert ${images.map(img => `"${img}"`).join(' ')} ${images.reverse().map(img => `"${img}"`).join(' ')} -resize ${targetSize} -delay ${delay} -loop 0 "${outputGif}"`;
    }

    await execPromise(convertCommand);

    const gifData = fs.readFileSync(outputGif);
    reply.type('image/gif').send(gifData);

    // Clean up temporary files
    images.forEach(img => fs.unlinkSync(img));
    fs.unlinkSync(outputGif);

  } catch (error) {
    reply.status(500).send({ error: 'Internal Server Error' });
  }
});

fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});