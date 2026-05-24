const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const fs = require('fs');
const { exec } = require('child_process');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

fastify.register(multipart);

fastify.post('/extract', async (request, reply) => {
  const data = await request.multipart();
  let videoFileName;
  let frameNumber;

  data.on('field', (field, value) => {
    if (field === 'videoFileName') {
      if (!/^[\w.-]+$/.test(value)) {
        return reply.status(400).send({ error: 'Invalid filename.' });
      }
      videoFileName = value;
    } else if (field === 'frameNumber') {
      frameNumber = parseInt(value, 10);
      if (isNaN(frameNumber) || frameNumber < 0) {
        return reply.status(400).send({ error: 'Invalid frame number.' });
      }
    }
  });

  data.on('file', async (field, file) => {
    const safeVideoFilePath = path.join(__dirname, 'uploads', `${uuidv4()}.mp4`);
    const writeStream = fs.createWriteStream(safeVideoFilePath);
    file.pipe(writeStream);

    writeStream.on('finish', async () => {
      const outputImagePath = path.join(__dirname, `frame_${frameNumber}.png`);
      const command = `ffmpeg -i "${safeVideoFilePath}" -vf "select=eq(n\\,${frameNumber.toString().replace(/[^0-9]/g, '')})" -vsync vfr "${outputImagePath}"`;

      exec(command, (error) => {
        if (error) {
          fs.unlinkSync(safeVideoFilePath);
          return reply.status(404).send({ error: `Frame at index ${frameNumber} could not be found.` });
        }

        fs.readFile(outputImagePath, (err, data) => {
          if (err) {
            fs.unlinkSync(safeVideoFilePath);
            return reply.status(404).send({ error: `Frame at index ${frameNumber} could not be found.` });
          }

          fs.unlinkSync(safeVideoFilePath);
          fs.unlinkSync(outputImagePath);
          reply.type('image/png').send(data);
        });
      });
    });
  });

  data.on('end', () => {
    // Handle end of multipart data
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