const fastify = require('fastify')({ logger: true });
const { execFile } = require('child_process');
const fs = require('fs').promises; // Use promises for async file operations
const path = require('path');

// Function to validate fileName
const isValidFileName = (fileName) => {
  const validFileNamePattern = /^[a-zA-Z0-9_.-]+$/; // Allow only alphanumeric characters, underscores, dashes, and dots
  return validFileNamePattern.test(fileName) && !fileName.includes('..');
};

// Function to sanitize file content
const sanitizeFileContent = (content) => {
  // Basic sanitization to remove potentially harmful characters
  return content.replace(/[\0\x1a]/g, ''); // Remove null bytes and control characters
};

fastify.post('/compile', async (request, reply) => {
  const { fileName, fileContent } = request.body;

  // Validate input
  if (!fileName || !fileContent) {
    return reply.status(400).send({ hasError: true, compilerError: 'Invalid input' });
  }

  // Validate fileName
  if (!isValidFileName(fileName)) {
    return reply.status(400).send({ hasError: true, compilerError: 'Invalid file name' });
  }

  // Sanitize file content
  const sanitizedContent = sanitizeFileContent(fileContent);
  const fileExtension = fileName.split('.').pop();
  const tempFilePath = path.join(__dirname, fileName);

  try {
    // Write the file content to the temporary file
    await fs.writeFile(tempFilePath, sanitizedContent);

    // Compile based on the file type
    let compileCommand;
    if (fileExtension === 'ts') {
      compileCommand = ['tsc', tempFilePath, '--noEmit'];
    } else if (fileExtension === 'cpp') {
      compileCommand = ['g++', tempFilePath, '-o', `${tempFilePath}.out`];
    } else {
      await fs.unlink(tempFilePath); // Clean up the temporary file
      return reply.status(400).send({ hasError: true, compilerError: 'Unsupported file type' });
    }

    // Execute the compile command
    const { stdout, stderr } = await new Promise((resolve, reject) => {
      execFile(compileCommand[0], compileCommand.slice(1), (error, stdout, stderr) => {
        if (error) {
          return reject(stderr.trim());
        }
        resolve({ stdout, stderr });
      });
    });

    // Clean up the temporary file
    await fs.unlink(tempFilePath);

    return reply.send({ hasError: false, compilerError: null, output: stdout.trim() });
  } catch (error) {
    // Clean up the temporary file in case of error
    try {
      await fs.unlink(tempFilePath);
    } catch (err) {
      // Ignore errors during cleanup
    }
    return reply.status(500).send({ hasError: true, compilerError: error });
  }
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