const fastify = require('fastify')({ logger: true });
const path = require('path');
const fs = require('fs');
const { execFile } = require('child_process');
const multipart = require('@fastify/multipart');

fastify.register(multipart);

fastify.post('/extract', async (request, reply) => {
  const data = await request.file();
  const { videoFileName, frameNumber } = data.fields;

  if (!videoFileName || !frameNumber || !data) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  const videoName = path.basename(videoFileName.value);
  const videoPath = path.join(__dirname, videoName);
  const framePath = path.join(__dirname, `frame_${frameNumber.value}.png`);

  if (!/\.mp4$/i.test(videoName)) {
    return reply.status(400).send({ error: 'Invalid file type. Only .mp4 files are allowed.' });
  }

  await new Promise((resolve, reject) => {
    const fileStream = fs.createWriteStream(videoPath);
    data.file.pipe(fileStream);
    data.file.on('end', resolve);
    data.file.on('error', reject);
  });

  const frameIndex = parseInt(frameNumber.value, 10);
  if (isNaN(frameIndex) || frameIndex < 0) {
    return reply.status(400).send({ error: 'Invalid frame number' });
  }

  execFile('ffmpeg', ['-i', videoPath, '-vf', `select=eq(n\\,${frameIndex})`, '-vframes', '1', framePath], (error) => {
    if (error) {
      return reply.status(404).send({ error: `Frame at index ${frameIndex} could not be found.` });
    }

    fs.readFile(framePath, (err, data) => {
      if (err) {
        return reply.status(500).send({ error: 'Error reading the extracted frame' });
      }

      reply.type('image/png').send(data);

      fs.unlink(videoPath, () => {});
      fs.unlink(framePath, () => {});
    });
  });
});

fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});