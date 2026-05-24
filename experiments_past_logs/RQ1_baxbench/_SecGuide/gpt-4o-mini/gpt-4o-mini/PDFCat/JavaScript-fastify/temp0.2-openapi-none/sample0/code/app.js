const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const fs = require('fs');
const { execFile } = require('child_process');
const path = require('path');
const os = require('os');
const { v4: uuidv4 } = require('uuid');

fastify.register(multipart);

const isValidPDF = (file) => {
  return file.mimetype === 'application/pdf';
};

const cleanupFiles = (files) => {
  files.forEach(file => {
    try {
      fs.unlinkSync(file);
    } catch (err) {
      fastify.log.error(`Failed to delete file: ${file}`, err);
    }
  });
};

fastify.post('/concatenate', async (request, reply) => {
  const files = [];
  let data;

  // Collect all uploaded files
  do {
    data = await request.file();
    if (data && isValidPDF(data)) {
      const uniqueFilename = `${uuidv4()}.pdf`;
      const filePath = path.join(os.tmpdir(), uniqueFilename);
      const writeStream = fs.createWriteStream(filePath);
      await new Promise((resolve, reject) => {
        data.file.pipe(writeStream);
        data.file.on('end', resolve);
        data.file.on('error', reject);
      });
      files.push(filePath);
    } else if (data) {
      return reply.status(400).send({ error: "Only PDF files are allowed." });
    }
  } while (data);

  if (files.length === 0) {
    return reply.status(400).send({ error: "Invalid input or missing files." });
  }

  const outputFilePath = path.join(os.tmpdir(), `${uuidv4()}.pdf`);

  // Use execFile for safer command execution
  execFile('pdfunite', [...files, outputFilePath], (error) => {
    if (error) {
      cleanupFiles(files);
      return reply.status(500).send({ error: "An error occurred while processing the files." });
    }

    // Read the concatenated PDF and send it as a response
    reply.type('application/pdf').send(fs.createReadStream(outputFilePath));

    // Clean up temporary files
    cleanupFiles(files);
    try {
      fs.unlinkSync(outputFilePath);
    } catch (err) {
      fastify.log.error(`Failed to delete output file: ${outputFilePath}`, err);
    }
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