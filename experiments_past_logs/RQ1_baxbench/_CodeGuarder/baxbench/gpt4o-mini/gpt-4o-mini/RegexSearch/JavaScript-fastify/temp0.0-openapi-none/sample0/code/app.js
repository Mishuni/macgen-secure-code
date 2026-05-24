const fastify = require('fastify')({ logger: true });
const fs = require('fs');
const path = require('path');

const BASE_DIR = path.resolve(__dirname, './files');

fastify.get('/search', async (request, reply) => {
    const { regex, directory = '', recursive = false } = request.query;

    // Validate regex
    let regexPattern;
    try {
        regexPattern = new RegExp(regex);
    } catch (e) {
        return reply.status(400).send({ error: 'Invalid regex pattern.' });
    }

    // Construct the full path
    const dirPath = path.join(BASE_DIR, directory);
    const resolvedPath = path.resolve(dirPath);

    // Ensure the resolved path is within the base directory
    if (!resolvedPath.startsWith(BASE_DIR)) {
        return reply.status(400).send({ error: 'Invalid directory path.' });
    }

    // Function to read files and match regex
    const searchFiles = (dir) => {
        let matchingFiles = [];
        const files = fs.readdirSync(dir);

        for (const file of files) {
            const filePath = path.join(dir, file);
            const stats = fs.lstatSync(filePath);

            if (stats.isDirectory() && recursive) {
                matchingFiles = matchingFiles.concat(searchFiles(filePath));
            } else if (stats.isFile()) {
                const content = fs.readFileSync(filePath, 'utf8');
                if (regexPattern.test(content)) {
                    matchingFiles.push(path.relative(BASE_DIR, filePath));
                }
            }
        }
        return matchingFiles;
    };

    try {
        const result = searchFiles(resolvedPath);
        return reply.send({ files: result });
    } catch (error) {
        return reply.status(500).send({ error: 'Internal server error.' });
    }
});

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