const fastify = require('fastify')({ logger: true });
const multipart = require('@fastify/multipart');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

fastify.register(multipart);

fastify.post('/extract', async (request, reply) => {
    const data = await request.form({ maxFiles: 1, maxFields: 2 });
    const { videoFileName, frameNumber } = data;

    if (!videoFileName || !frameNumber) {
        return reply.status(400).send({ error: 'Missing videoFileName or frameNumber' });
    }

    const videoFile = data.video;
    const uploadPath = path.join(__dirname, videoFileName);

    // Save the uploaded video file
    await videoFile.toFile(uploadPath);

    const outputImagePath = path.join(__dirname, `frame_${frameNumber}.png`);
    const ffmpegCommand = `ffmpeg -i "${uploadPath}" -vf "select=eq(n\\,${frameNumber})" -vframes 1 "${outputImagePath}"`;

    return new Promise((resolve, reject) => {
        exec(ffmpegCommand, (error, stdout, stderr) => {
            if (error) {
                fs.unlinkSync(uploadPath); // Clean up uploaded video
                if (stderr.includes('Invalid frame')) {
                    return reject(reply.status(404).send({ error: `Frame at index ${frameNumber} could not be found.` }));
                }
                return reject(reply.status(500).send({ error: 'Error processing video' }));
            }

            // Read the extracted image and send it as a response
            fs.readFile(outputImagePath, (err, imageData) => {
                if (err) {
                    return reject(reply.status(500).send({ error: 'Error reading extracted image' }));
                }

                // Clean up files
                fs.unlinkSync(uploadPath);
                fs.unlinkSync(outputImagePath);

                reply.type('image/png').send(imageData);
                resolve();
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