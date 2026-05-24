const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

fastify.register(multipart);

fastify.post('/convert', async (request, reply) => {
    const data = await request.file();
    
    // Validate file type
    if (!data || data.mimetype !== 'application/pdf') {
        return reply.status(400).send({ error: 'Invalid input or missing file' });
    }

    const tempFilePath = path.join(__dirname, 'uploads', data.filename);
    
    // Create uploads directory if it doesn't exist
    if (!fs.existsSync(path.join(__dirname, 'uploads'))) {
        fs.mkdirSync(path.join(__dirname, 'uploads'));
    }

    // Pipe the file to a temporary location
    await new Promise((resolve, reject) => {
        const writeStream = fs.createWriteStream(tempFilePath);
        data.file.pipe(writeStream);
        data.file.on('end', resolve);
        data.file.on('error', reject);
    });

    // Use pdftotext to convert PDF to text
    const outputFilePath = path.join(__dirname, 'uploads', `${data.filename}.txt`);
    const command = `pdftotext "${tempFilePath}" "${outputFilePath}"`;

    return new Promise((resolve, reject) => {
        exec(command, (error) => {
            // Clean up the temporary PDF file
            fs.unlink(tempFilePath, (err) => {
                if (err) {
                    fastify.log.error(err);
                }
            });

            if (error) {
                return reject(reply.status(500).send({ error: 'Conversion failed' }));
            }

            // Read the converted text file
            fs.readFile(outputFilePath, 'utf8', (err, data) => {
                if (err) {
                    return reject(reply.status(500).send({ error: 'Failed to read converted text' }));
                }

                // Clean up the text file
                fs.unlink(outputFilePath, (err) => {
                    if (err) {
                        fastify.log.error(err);
                    }
                });

                resolve(reply.status(200).send(data));
            });
        });
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