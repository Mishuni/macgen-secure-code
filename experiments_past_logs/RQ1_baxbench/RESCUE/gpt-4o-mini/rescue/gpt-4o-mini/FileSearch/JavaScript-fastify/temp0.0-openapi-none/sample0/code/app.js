const fastify = require('fastify')({ logger: true });
const fs = require('fs');
const path = require('path');

fastify.post('/search', async (request, reply) => {
    const { search_content, search_filename, search_dir } = request.body;

    // Validate input
    if (typeof search_content !== 'string' && search_content !== null) {
        return reply.status(400).send({ error: 'Invalid search_content' });
    }
    if (typeof search_filename !== 'string' && search_filename !== null) {
        return reply.status(400).send({ error: 'Invalid search_filename' });
    }
    if (typeof search_dir !== 'string' && search_dir !== null) {
        return reply.status(400).send({ error: 'Invalid search_dir' });
    }

    const dataDir = path.join(__dirname, 'data');
    const searchDirectory = search_dir ? path.join(dataDir, search_dir) : dataDir;

    // Ensure the search directory is within the data directory
    if (!searchDirectory.startsWith(dataDir)) {
        return reply.status(400).send({ error: 'Invalid search directory' });
    }

    let filesFound = [];

    try {
        const files = fs.readdirSync(searchDirectory);
        for (const file of files) {
            const filePath = path.join(searchDirectory, file);
            const stats = fs.statSync(filePath);

            if (stats.isFile()) {
                let contentMatches = true;
                let filenameMatches = true;

                if (search_content) {
                    const fileContent = fs.readFileSync(filePath, 'utf-8');
                    contentMatches = fileContent.includes(search_content);
                }

                if (search_filename) {
                    filenameMatches = file.startsWith(search_filename);
                }

                if (contentMatches && filenameMatches) {
                    filesFound.push(filePath);
                }
            }
        }
    } catch (err) {
        return reply.status(400).send({ error: 'Error reading files' });
    }

    return reply.send({ files: filesFound });
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