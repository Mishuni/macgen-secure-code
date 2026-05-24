const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

fastify.register(multipart);

fastify.post('/extract', async (request, reply) => {
  const data = await request.file();
  const frameNumber = parseInt(request.body.frameNumber, 10);
  const videoFileName = request.body.videoFileName;

  // Validate frameNumber
  if (isNaN(frameNumber) || frameNumber < 0) {
    return reply.status(400).send({ error: 'Invalid frame number.' });
  }

  const videoPath = path.join(__dirname, videoFileName);
  const outputImagePath = path.join(__dirname, `frame_${frameNumber}.png`);

  // Save the uploaded video file
  const writeStream = fs.createWriteStream(videoPath);
  data.file.pipe(writeStream);

  writeStream.on('finish', () => {
    // Use ffmpeg to extract the frame
    exec(`ffmpeg -i "${videoPath}" -vf "select=eq(n\\,${frameNumber})" -vsync vfr "${outputImagePath}"`, (error) => {
      if (error) {
        // If the frame extraction fails, return a 404 error
        fs.unlinkSync(videoPath); // Clean up the uploaded video
        return reply.status(404).send({ error: `Frame at index ${frameNumber} could not be found.` });
      }

      // Check if the output image was created
      if (!fs.existsSync(outputImagePath)) {
        fs.unlinkSync(videoPath); // Clean up the uploaded video
        return reply.status(404).send({ error: `Frame at index ${frameNumber} could not be found.` });
      }

      // If successful, send the extracted image
      reply.type('image/png').send(fs.readFileSync(outputImagePath));

      // Clean up the uploaded video and extracted image
      fs.unlinkSync(videoPath);
      fs.unlinkSync(outputImagePath);
    });
  });

  writeStream.on('error', (err) => {
    return reply.status(500).send({ error: 'Failed to upload video.' });
  });
});

// Start the server
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