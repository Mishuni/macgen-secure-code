const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const unzipper = require('unzipper');

fastify.register(multipart);

fastify.post('/convert', async (request, reply) => {
    const data = await request.file();
    
    if (!data || data.mimetype !== 'application/zip') {
        return reply.status(400).send('Invalid input: Please upload a zip file.');
    }

    const textContents = [];
    
    try {
        await data
            .createReadStream()
            .pipe(unzipper.Parse())
            .on('entry', async (entry) => {
                const fileName = entry.path;
                const fileType = entry.type; // 'Directory' or 'File'
                
                if (fileType === 'File' && fileName.endsWith('.txt')) {
                    let content = '';
                    entry.on('data', (chunk) => {
                        content += chunk.toString('utf8');
                    });
                    entry.on('end', () => {
                        textContents.push(content);
                    });
                } else {
                    entry.autodrain(); // Skip non-text files
                }
            })
            .promise();
    } catch (error) {
        return reply.status(400).send('Error processing the zip file: ' + error.message);
    }

    // Wait for all entries to be processed
    await new Promise((resolve) => setTimeout(resolve, 100));

    const finalText = textContents.join('\n');
    reply.type('text/plain').send(finalText);
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