const fastify = require('fastify')({ logger: true });
const path = require('path');
const fs = require('fs');
const os = require('os');
const unzipper = require('unzipper');
const { pipeline } = require('stream');
const util = require('util');
const pump = util.promisify(pipeline);
const multipart = require('@fastify/multipart');

// Register multipart plugin
fastify.register(multipart);

// Utility function to sanitize file paths
function sanitizeFilePath(filePath) {
  const safeBase = path.resolve(os.tmpdir());
  const resolvedPath = path.resolve(filePath);
  if (!resolvedPath.startsWith(safeBase)) {
    throw new Error('Invalid file path');
  }
  return resolvedPath;
}

// POST /convert endpoint
fastify.post('/convert', async (req, reply) => {
  const data = await req.file();

  // Validate that a file was uploaded
  if (!data || data.fieldname !== 'file') {
    reply.code(400).send('Invalid input: No file uploaded');
    return;
  }

  // Ensure the uploaded file is a zip file
  const fileType = data.filename.split('.').pop().toLowerCase();
  if (fileType !== 'zip') {
    reply.code(400).send('Invalid input: Only zip files are allowed');
    return;
  }

  // Create a temporary directory for processing
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'zip-to-txt-'));
  const outputFilePath = path.join(tempDir, 'output.txt');

  try {
    // Extract the zip file
    const extractDir = path.join(tempDir, 'extracted');
    fs.mkdirSync(extractDir);

    await pump(
      data.file,
      unzipper.Extract({ path: extractDir })
    );

    // Concatenate all text files in the zip
    const files = fs.readdirSync(extractDir);
    const outputStream = fs.createWriteStream(outputFilePath, { flags: 'w' });

    for (const file of files) {
      const filePath = path.join(extractDir, file);

      // Sanitize file path to prevent directory traversal
      const sanitizedPath = sanitizeFilePath(filePath);

      // Only process .txt files
      if (path.extname(sanitizedPath).toLowerCase() === '.txt') {
        const fileContents = fs.readFileSync(sanitizedPath, 'utf8');
        outputStream.write(fileContents + '\n');
      }
    }

    outputStream.end();

    // Send the concatenated text file as the response
    reply.type('text/plain').send(fs.createReadStream(outputFilePath));
  } catch (err) {
    fastify.log.error(err);
    reply.code(500).send('Internal Server Error');
  } finally {
    // Clean up temporary files and directories
    fs.rmSync(tempDir, { recursive: true, force: true });
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