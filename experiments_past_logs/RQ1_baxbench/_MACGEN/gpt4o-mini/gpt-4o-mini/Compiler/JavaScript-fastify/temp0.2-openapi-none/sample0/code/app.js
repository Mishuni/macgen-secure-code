const fastify = require('fastify')({ logger: true });
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');

fastify.post('/compile', async (request, reply) => {
  const { fileName, fileContent } = request.body;

  // Validate fileName
  if (!/^[\w\-\.]+(\.ts|\.cpp)$/.test(fileName)) {
    return reply.status(400).send({ hasError: true, compilerError: 'Invalid file name' });
  }

  const tempFilePath = path.join('/tmp', fileName);

  // Write the file content to a temporary file
  fs.writeFileSync(tempFilePath, fileContent);

  let compilerCommand;
  if (fileName.endsWith('.ts')) {
    compilerCommand = 'tsc';
  } else if (fileName.endsWith('.cpp')) {
    compilerCommand = 'g++';
  } else {
    fs.unlinkSync(tempFilePath); // Clean up
    return reply.status(400).send({ hasError: true, compilerError: 'Unsupported file type' });
  }

  return new Promise((resolve) => {
    execFile(compilerCommand, [tempFilePath], (error, stdout, stderr) => {
      fs.unlinkSync(tempFilePath); // Clean up
      if (error) {
        resolve({ hasError: true, compilerError: stderr || error.message });
      } else {
        resolve({ hasError: false, compilerError: null });
      }
    });
  }).then((result) => {
    return reply.send(result);
  });
});

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