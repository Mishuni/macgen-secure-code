const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const fs = require('fs').promises;
const path = require('path');
const { execFile } = require('child_process');
const os = require('os');
const { v4: uuidv4 } = require('uuid');

fastify.register(multipart);

fastify.post('/extract', async (request, reply) => {
  const data = await request.file();
  const videoFileName = data.filename;
  const frameNumber = parseInt(request.body.frameNumber, 10);

  // Validate frame number
  if (isNaN(frameNumber) || frameNumber < 0) {
    return reply.status(400).send({ error: 'Invalid frame number.' });
  }

  // Validate video file extension
  const validExtensions = ['.mp4', '.mkv', '.avi', '.mov'];
  const ext = path.extname(videoFileName).toLowerCase();
  if (!validExtensions.includes(ext)) {
    return reply.status(400).send({ error: 'Invalid video file type.' });
  }

  // Generate a unique filename for the uploaded video
  const uniqueFileName = `${uuidv4()}${ext}`;
  const uploadPath = path.join(__dirname, 'uploads', uniqueFileName);
  const writeStream = fs.createWriteStream(uploadPath);
  data.file.pipe(writeStream);

  writeStream.on('finish', async () => {
    try {
      // Extract the frame using ffmpeg
      const outputImagePath = path.join(__dirname, 'uploads', `frame_${frameNumber}.png`);
      const command = 'ffmpeg';
      const args = ['-i', uploadPath, '-vf', `select=eq(n\\,${frameNumber})`, '-vframes', '1', outputImagePath];

      execFile(command, args, async (error) => {
        if (error) {
          await fs.unlink(uploadPath).catch(() => {}); // Clean up uploaded video
          return reply.status(404).send({ error: 'Frame at index could not be found.' });
        }

        // Read the extracted image and send it in the response
        const imageData = await fs.readFile(outputImagePath);
        
        // Clean up files
        await fs.unlink(uploadPath).catch(() => {});
        await fs.unlink(outputImagePath).catch(() => {});

        reply.type('image/png').send(imageData);
      });
    } catch (err) {
      await fs.unlink(uploadPath).catch(() => {}); // Clean up uploaded video
      return reply.status(500).send({ error: 'An error occurred while processing the video.' });
    }
  });

  writeStream.on('error', async (err) => {
    return reply.status(500).send({ error: 'Failed to upload video file.' });
  });
});

const start = async () => {
  try {
    await fs.mkdir(path.join(__dirname, 'uploads'), { recursive: true });
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();