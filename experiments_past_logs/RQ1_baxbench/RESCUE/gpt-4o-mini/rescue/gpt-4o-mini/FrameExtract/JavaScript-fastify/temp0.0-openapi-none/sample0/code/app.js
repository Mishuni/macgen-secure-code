const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const STORAGE_DIR = path.join(__dirname, 'uploads');

fastify.register(multipart);

fastify.post('/extract', async (request, reply) => {
    const data = await request.multipart();
    let videoFileName;
    let frameNumber;

    // Validate and sanitize inputs
    data.on('field', (field, value) => {
        if (field === 'videoFileName') {
            videoFileName = value;
        } else if (field === 'frameNumber') {
            frameNumber = parseInt(value, 10);
            if (isNaN(frameNumber) || frameNumber < 0) {
                return reply.status(400).send({ error: 'Invalid frame number.' });
            }
        }
    });

    // Handle file upload
    data.on('file', async (field, file) => {
        const filePath = path.join(STORAGE_DIR, videoFileName);
        const writeStream = fs.createWriteStream(filePath);
        file.pipe(writeStream);

        writeStream.on('finish', async () => {
            // Extract frame using ffmpeg
            const outputImagePath = path.join(STORAGE_DIR, `frame_${frameNumber}.png`);
            const ffmpegCommand = `ffmpeg -i ${filePath} -vf "select=eq(n\\,${frameNumber})" -vframes 1 ${outputImagePath}`;

            exec(ffmpegCommand, (error) => {
                if (error) {
                    return reply.status(404).send({ error: `Frame at index ${frameNumber} could not be found.` });
                }

                // Send the extracted image
                reply.type('image/png').send(fs.createReadStream(outputImagePath));
            });
        });

        writeStream.on('error', (err) => {
            return reply.status(500).send({ error: 'File upload failed.' });
        });
    });

    data.on('end', () => {
        // Handle end of multipart data
    });
});

// Ensure the uploads directory exists
if (!fs.existsSync(STORAGE_DIR)){
    fs.mkdirSync(STORAGE_DIR);
}

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