const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const unzipper = require('unzipper');
const { Readable } = require('stream');

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB limit
const ALLOWED_MIME_TYPES = ['text/plain', 'application/octet-stream']; // Allow text/plain and generic binary

fastify.register(multipart);

fastify.post('/convert', async (request, reply) => {
  const data = await request.file();

  if (!data) {
    return reply.status(400).send('Invalid input');
  }

  // Check file size
  if (data.fileSize > MAX_FILE_SIZE) {
    return reply.status(400).send('File size exceeds limit');
  }

  let textContent = '';

  try {
    await data
      .pipe(unzipper.Parse())
      .on('entry', async (entry) => {
        const fileName = entry.path;
        const type = entry.type; // 'Directory' or 'File'

        if (type === 'File') {
          // Validate file type using MIME type
          const mimeType = entry._header.split(';')[0].split(':')[1].trim();
          if (!ALLOWED_MIME_TYPES.includes(mimeType) || !fileName.endsWith('.txt')) {
            entry.autodrain(); // Skip non-text files
            return;
          }

          // Process file in a streaming manner
          const chunks = [];
          entry.on('data', (chunk) => {
            chunks.push(chunk);
          });

          entry.on('end', () => {
            const content = Buffer.concat(chunks).toString('utf-8');

            // Basic content validation (e.g., check for executable code)
            if (!containsMaliciousContent(content)) {
              textContent += content + '\n';
            } else {
              fastify.log.warn(`Malicious content detected in file: ${fileName}`);
            }
          });
        } else {
          entry.autodrain(); // Skip directories
        }
      })
      .promise();
  } catch (err) {
    fastify.log.error(err);
    return reply.status(400).send('Error processing zip file');
  }

  return reply.type('text/plain').send(textContent);
});

// Simple content validation function
function containsMaliciousContent(content) {
  // Implement basic checks for malicious patterns (e.g., script tags)
  const maliciousPatterns = /<script>|eval\(|exec\(|os\.|require\(/i;
  return maliciousPatterns.test(content);
}

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