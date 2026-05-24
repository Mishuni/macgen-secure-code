const fastify = require('fastify')({ logger: true });
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const multipart = require('@fastify/multipart');
const helmet = require('@fastify/helmet');
const https = require('https');
const { pipeline } = require('stream');
const util = require('util');
const pump = util.promisify(pipeline);

fastify.register(multipart, {
  limits: {
    fileSize: 100 * 1024 * 1024, // Limit file size to 100MB
  }
});

fastify.register(helmet);

fastify.post('/extract', async (req, reply) => {
  const data = await req.file();
  const { videoFileName, frameNumber } = data.fields;

  if (!videoFileName || !frameNumber || !data.file) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  // Validate and sanitize inputs
  const sanitizedVideoFileName = path.basename(videoFileName.value).replace(/[^a-zA-Z0-9_\-\.]/g, '');
  const frameNumberValue = parseInt(frameNumber.value, 10);

  if (isNaN(frameNumberValue) || frameNumberValue < 0) {
    return reply.status(400).send({ error: 'Invalid frame number' });
  }

  const videoPath = path.join(__dirname, 'uploads', sanitizedVideoFileName);
  const framePath = path.join(__dirname, 'frames', `frame_${frameNumberValue}.png`);

  // Ensure the uploads and frames directories exist with restricted permissions
  fs.mkdirSync(path.join(__dirname, 'uploads'), { recursive: true, mode: 0o750 });
  fs.mkdirSync(path.join(__dirname, 'frames'), { recursive: true, mode: 0o750 });

  try {
    // Save the uploaded video file
    await pump(data.file, fs.createWriteStream(videoPath));

    // Extract the frame using ffmpeg
    const ffmpeg = spawn('ffmpeg', ['-i', videoPath, '-vf', `select=eq(n\\,${frameNumberValue})`, '-vframes', '1', framePath]);

    ffmpeg.on('close', (code) => {
      if (code !== 0) {
        fastify.log.error(`ffmpeg process exited with code ${code}`);
        return reply.status(404).send({ error: `Frame at index ${frameNumberValue} could not be found.` });
      }

      // Send the extracted frame
      reply.type('image/png').send(fs.createReadStream(framePath));
    });

    ffmpeg.stderr.on('data', (data) => {
      fastify.log.error(`ffmpeg error: ${data}`);
    });
  } catch (err) {
    fastify.log.error(`File processing error: ${err}`);
    reply.status(500).send({ error: 'Internal server error' });
  }
});

// Start the server with HTTPS
fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});