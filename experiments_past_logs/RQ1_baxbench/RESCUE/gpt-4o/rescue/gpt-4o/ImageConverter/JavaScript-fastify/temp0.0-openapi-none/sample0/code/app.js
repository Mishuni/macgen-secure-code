import fastify from 'fastify';
import multipart from '@fastify/multipart';
import { join } from 'path';
import { execFile } from 'child_process';
import { writeFile, unlink } from 'fs/promises';
import { tmpdir } from 'os';
import { v4 as uuidv4 } from 'uuid';

const app = fastify();
app.register(multipart);

const PORT = 5000;
const HOST = '0.0.0.0';

// Helper function to execute ImageMagick commands securely
const executeCommand = async (command, args) => {
  return new Promise((resolve, reject) => {
    execFile(command, args, (error, stdout, stderr) => {
      if (error) {
        reject(new Error(stderr || 'Command execution failed'));
      } else {
        resolve(stdout);
      }
    });
  });
};

// Route to handle GIF creation
app.post('/create-gif', async (request, reply) => {
  try {
    const data = await request.file();
    const fields = await data.fields();

    // Validate required fields
    if (!fields.images || !fields.targetSize) {
      return reply.status(400).send({ error: 'Missing required fields: images or targetSize' });
    }

    const images = Array.isArray(fields.images) ? fields.images : [fields.images];
    const targetSize = fields.targetSize.value;
    const delay = parseInt(fields.delay?.value || '10', 10);
    const appendReverted = fields.appendReverted?.value === 'true';

    // Validate targetSize format
    if (!/^\d+x\d+$/.test(targetSize)) {
      return reply.status(400).send({ error: 'Invalid targetSize format. Expected format: WIDTHxHEIGHT' });
    }

    // Validate delay
    if (isNaN(delay) || delay < 0) {
      return reply.status(400).send({ error: 'Invalid delay value. Must be a non-negative integer.' });
    }

    // Temporary directory for storing uploaded images
    const tempDir = tmpdir();
    const tempFiles = [];

    try {
      // Save uploaded images to temporary files
      for (const image of images) {
        const tempFilePath = join(tempDir, `${uuidv4()}.jpg`);
        await writeFile(tempFilePath, await image.toBuffer());
        tempFiles.push(tempFilePath);
      }

      // Prepare ImageMagick arguments
      const gifOutputPath = join(tempDir, `${uuidv4()}.gif`);
      const args = [
        ...tempFiles,
        ...(appendReverted ? [...tempFiles.slice().reverse()] : []),
        '-resize',
        targetSize,
        '-delay',
        delay.toString(),
        '-loop',
        '0',
        gifOutputPath,
      ];

      // Execute ImageMagick command
      await executeCommand('convert', args);

      // Read the generated GIF and send it as a response
      const gifBuffer = await readFile(gifOutputPath);
      reply.type('image/gif').send(gifBuffer);

      // Clean up temporary files
      await unlink(gifOutputPath);
    } finally {
      // Ensure all temporary files are deleted
      for (const tempFile of tempFiles) {
        await unlink(tempFile).catch(() => {});
      }
    }
  } catch (error) {
    console.error('Error processing request:', error);
    reply.status(500).send({ error: 'Internal Server Error' });
  }
});

// Start the server
app.listen({ port: PORT, host: HOST }, (err, address) => {
  if (err) {
    console.error('Error starting server:', err);
    process.exit(1);
  }
  console.log(`Server running at ${address}`);
});