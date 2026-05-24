const fastify = require('fastify')({ logger: true });
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

fastify.post('/compile', async (request, reply) => {
  const { fileName, fileContent } = request.body;

  // Validate input
  if (!fileName || !fileContent) {
    return reply.status(400).send({ hasError: true, compilerError: 'fileName and fileContent are required.' });
  }

  // Determine the file extension
  const fileExtension = fileName.split('.').pop();
  const allowedExtensions = ['ts', 'cpp'];

  if (!allowedExtensions.includes(fileExtension)) {
    return reply.status(400).send({ hasError: true, compilerError: 'Unsupported file type' });
  }

  // Create a temporary file
  const tempFilePath = path.join(__dirname, fileName);

  try {
    // Write the file content to the temporary file
    fs.writeFileSync(tempFilePath, fileContent);
  } catch (err) {
    return reply.status(500).send({ hasError: true, compilerError: 'Failed to write temporary file.' });
  }

  // Compile based on the file extension
  let compileCommand;
  if (fileExtension === 'ts') {
    compileCommand = `tsc ${tempFilePath} --noEmit`;
  } else if (fileExtension === 'cpp') {
    compileCommand = `g++ ${tempFilePath} -o ${tempFilePath}.out`;
  }

  return new Promise((resolve) => {
    exec(compileCommand, (error, stdout, stderr) => {
      // Clean up the temporary file
      fs.unlinkSync(tempFilePath);

      if (error) {
        return resolve({ hasError: true, compilerError: stderr.trim() });
      }
      return resolve({ hasError: false, compilerError: null });
    });
  }).then((result) => {
    reply.send(result);
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