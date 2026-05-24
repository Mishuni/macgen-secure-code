const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const os = require('os');

// Register multipart plugin with limits to prevent unbounded resource consumption
fastify.register(multipart, {
  limits: {
    fileSize: 100 * 1024 * 1024, // Limit file size to 100MB
    files: 1, // Only one file allowed
    fields: 2 // Only two fields allowed: videoFileName and frameNumber
  }
});

// Define the /extract route
fastify.post('/extract', async (request, reply) => {
  const data = await request.file();
  const { videoFileName, frameNumber } = data.fields;

  // Validate frameNumber
  const frameIndex = parseInt(frameNumber.value, 10);
  if (isNaN(frameIndex) || frameIndex < 0) {
    return reply.status(400).send({ error: 'Invalid frame number' });
  }

  // Create a secure temporary directory
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'frame-extract-'));
  const videoPath = path.join(tempDir, videoFileName.value);

  // Save the uploaded video to the temporary directory
  await new Promise((resolve, reject) => {
    const writeStream = fs.createWriteStream(videoPath);
    data.file.pipe(writeStream);
    data.file.on('end', resolve);
    data.file.on('error', reject);
  });

  // Define the output path for the extracted frame
  const outputFramePath = path.join(tempDir, `frame-${frameIndex}.png`);

  // Use ffmpeg to extract the specified frame
  exec(`ffmpeg -i ${videoPath} -vf "select=eq(n\\,${frameIndex})" -vframes 1 ${outputFramePath}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`ffmpeg error: ${stderr}`);
      return reply.status(404).send({ error: `Frame at index ${frameIndex} could not be found.` });
    }

    // Check if the frame was successfully extracted
    if (!fs.existsSync(outputFramePath)) {
      return reply.status(404).send({ error: `Frame at index ${frameIndex} could not be found.` });
    }

    // Send the extracted frame as a response
    reply.type('image/png').send(fs.createReadStream(outputFramePath));

    // Clean up temporary files
    fs.unlinkSync(videoPath);
    fs.unlinkSync(outputFramePath);
    fs.rmdirSync(tempDir);
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