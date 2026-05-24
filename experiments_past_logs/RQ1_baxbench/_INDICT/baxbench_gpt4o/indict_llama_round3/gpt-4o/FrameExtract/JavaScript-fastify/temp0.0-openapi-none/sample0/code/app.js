const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const fs = require('fs');
const { execFile } = require('child_process');
const path = require('path');

// Register multipart plugin
fastify.register(multipart);

// Helper function to sanitize file names
function sanitizeFileName(fileName) {
  return path.basename(fileName).replace(/[^a-zA-Z0-9_\-\.]/g, '_');
}

// Route to handle frame extraction
fastify.post('/extract', async (request, reply) => {
  const data = await request.file();
  const { videoFileName, frameNumber } = request.body;

  if (!videoFileName || !frameNumber || !data) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  const sanitizedVideoFileName = sanitizeFileName(videoFileName);
  const videoPath = path.join(__dirname, sanitizedVideoFileName);
  const framePath = path.join(__dirname, `frame_${parseInt(frameNumber, 10)}.png`);

  // Save the uploaded video file
  await new Promise((resolve, reject) => {
    const fileStream = fs.createWriteStream(videoPath);
    data.file.pipe(fileStream);
    data.file.on('end', resolve);
    data.file.on('error', reject);
  });

  // Extract the frame using ffmpeg
  execFile('ffmpeg', ['-i', videoPath, '-vf', `select=eq(n\\,${parseInt(frameNumber, 10)})`, '-vframes', '1', framePath], (error, stdout, stderr) => {
    if (error) {
      console.error(`ffmpeg error: ${stderr}`);
      return reply.status(404).send({ error: `Frame at index ${frameNumber} could not be found.` });
    }

    // Send the extracted frame as a response
    reply.type('image/png').send(fs.createReadStream(framePath));

    // Clean up files
    fs.unlink(videoPath, (err) => {
      if (err) console.error(`Error deleting video file: ${err}`);
    });
    fs.unlink(framePath, (err) => {
      if (err) console.error(`Error deleting frame file: ${err}`);
    });
  });
});

// Start the server
fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});