const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// Register multipart support with limits
fastify.register(multipart, {
  limits: {
    fileSize: 10 * 1024 * 1024, // 10 MB file size limit
    files: 1, // Only one file allowed per request
    fields: 1 // Only one field allowed per request
  }
});

// Define the /convert route
fastify.post('/convert', async (request, reply) => {
  const data = await request.file();
  
  if (!data || data.fieldname !== 'file') {
    return reply.status(400).send({ error: 'Bad Request - Invalid input or missing file' });
  }

  const filePath = path.join(__dirname, 'uploads', data.filename);
  const outputFilePath = path.join(__dirname, 'uploads', `${data.filename}.txt`);

  try {
    // Save the uploaded file
    await new Promise((resolve, reject) => {
      const fileStream = fs.createWriteStream(filePath);
      data.file.pipe(fileStream);
      data.file.on('end', resolve);
      data.file.on('error', reject);
    });

    // Validate the file type (basic check for PDF)
    if (!filePath.endsWith('.pdf')) {
      fs.unlinkSync(filePath);
      return reply.status(400).send({ error: 'Bad Request - Only PDF files are allowed' });
    }

    // Extract text from PDF using pdftotext
    await new Promise((resolve, reject) => {
      exec(`pdftotext "${filePath}" "${outputFilePath}"`, (error) => {
        if (error) {
          reject(error);
        } else {
          resolve();
        }
      });
    });

    // Read the extracted text
    const textContent = fs.readFileSync(outputFilePath, 'utf8');

    // Clean up files
    fs.unlinkSync(filePath);
    fs.unlinkSync(outputFilePath);

    // Send the extracted text as response
    reply.type('text/plain').send(textContent);
  } catch (error) {
    // Clean up files in case of error
    if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
    if (fs.existsSync(outputFilePath)) fs.unlinkSync(outputFilePath);

    // Log the error and send a 500 response
    fastify.log.error(error);
    reply.status(500).send({ error: 'Internal Server Error - Conversion failed' });
  }
});

// Start the server
fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});