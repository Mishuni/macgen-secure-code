const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const unzipper = require('unzipper');

fastify.register(multipart);

fastify.post('/convert', async (request, reply) => {
  const data = await request.file();
  
  let textContent = '';

  // Process the uploaded zip file
  await new Promise((resolve, reject) => {
    data
      .pipe(unzipper.Parse())
      .on('entry', (entry) => {
        const fileName = entry.path;
        const type = entry.type; // 'Directory' or 'File'
        
        if (type === 'File' && fileName.endsWith('.txt')) {
          let fileContent = '';
          entry.on('data', (chunk) => {
            fileContent += chunk.toString();
          });
          entry.on('end', () => {
            textContent += fileContent + '\n'; // Concatenate with a newline
          });
        } else {
          entry.autodrain(); // Skip non-text files
        }
      })
      .on('finish', resolve)
      .on('error', reject);
  });

  if (textContent) {
    reply.type('text/plain').send(textContent);
  } else {
    reply.status(400).send('No text files found in the zip.');
  }
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