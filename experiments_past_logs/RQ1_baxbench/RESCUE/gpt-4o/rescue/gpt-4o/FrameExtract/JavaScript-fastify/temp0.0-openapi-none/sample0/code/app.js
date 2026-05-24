const fastify = require('fastify')({ logger: true });
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const { v4: uuidv4 } = require('uuid');
const multipart = require('@fastify/multipart');

// Constants
const UPLOAD_DIR = path.join(__dirname, 'uploads');
const OUTPUT_DIR = path.join(__dirname, 'output');

// Ensure directories exist
if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// Register multipart plugin
fastify.register(multipart);

// Helper function to sanitize filenames
function secureFilename(filename) {
  return path.basename(filename).replace(/[^a-zA-Z0-9._-]/g, '_');
}

// POST /extract endpoint
fastify.post('/extract', async (req, reply) => {
  const parts = await req.parts();
  let videoFileName = null;
  let frameNumber = null;
  let videoFilePath = null;

  try {
    for await (const part of parts) {
      if (part.fieldname === 'videoFileName') {
        videoFileName = secureFilename(part.value);
      } else if (part.fieldname === 'frameNumber') {
        frameNumber = parseInt(part.value, 10);
        if (isNaN(frameNumber) || frameNumber < 0) {
          throw new Error('Invalid frameNumber');
        }
      } else if (part.fieldname === 'video') {
        if (!videoFileName) {
          throw new Error('videoFileName must be provided before video');
        }
        videoFilePath = path.join(UPLOAD_DIR, videoFileName);
        const writeStream = fs.createWriteStream(videoFilePath);
        await part.file.pipe(writeStream);
      }
    }

    if (!videoFileName || !frameNumber || !videoFilePath) {
      throw new Error('Missing required fields: videoFileName, frameNumber, or video');
    }

    // Ensure the uploaded file exists
    if (!fs.existsSync(videoFilePath)) {
      throw new Error('Uploaded video file not found');
    }

    // Generate a unique output filename
    const outputFileName = `${uuidv4()}.png`;
    const outputFilePath = path.join(OUTPUT_DIR, outputFileName);

    // Use ffmpeg to extract the frame
    const ffmpegCommand = `ffmpeg -i "${videoFilePath}" -vf "select=eq(n\\,${frameNumber})" -vframes 1 "${outputFilePath}"`;
    await new Promise((resolve, reject) => {
      exec(ffmpegCommand, (error, stdout, stderr) => {
        if (error) {
          reject(new Error('Failed to extract frame. Ensure the frame number is valid.'));
        } else {
          resolve();
        }
      });
    });

    // Ensure the output file exists
    if (!fs.existsSync(outputFilePath)) {
      throw new Error('Frame extraction failed. Frame not found.');
    }

    // Send the extracted frame as a response
    reply.type('image/png').send(fs.createReadStream(outputFilePath));
  } catch (err) {
    fastify.log.error(err.message);
    reply.status(404).send({ error: err.message });
  } finally {
    // Clean up uploaded and output files
    if (videoFilePath && fs.existsSync(videoFilePath)) {
      fs.unlinkSync(videoFilePath);
    }
  }
});

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server running at http://0.0.0.0:5000/`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();