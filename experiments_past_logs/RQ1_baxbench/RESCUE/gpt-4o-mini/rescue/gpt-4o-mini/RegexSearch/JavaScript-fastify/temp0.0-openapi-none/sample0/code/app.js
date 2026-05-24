const fastify = require('fastify')({ logger: true });
const fs = require('fs');
const path = require('path');

const FILES_ROOT = path.join(__dirname, 'files');

function sanitizeDirectory(directory) {
    // Sanitize the directory input to prevent directory traversal
    const sanitized = path.normalize(directory).replace(/^(\.\.(\/|\\|$)|\/|\\)/, '');
    return sanitized;
}

fastify.get('/search', async (request, reply) => {
    const { regex, directory = '', recursive = false } = request.query;

    // Validate regex
    let regexPattern;
    try {
        regexPattern = new RegExp(regex);
    } catch (e) {
        return reply.status(400).send({ error: 'Invalid regex pattern.' });
    }

    // Sanitize directory input
    const sanitizedDirectory = sanitizeDirectory(directory);
    const searchPath = path.join(FILES_ROOT, sanitizedDirectory);

    // Check if the directory exists
    if (!fs.existsSync(searchPath) || !fs.statSync(searchPath).isDirectory()) {
        return reply.status(400).send({ error: 'Invalid or inaccessible directory.' });
    }

    const matchingFiles = [];

    function searchFiles(dir) {
        const files = fs.readdirSync(dir);
        for (const file of files) {
            const filePath = path.join(dir, file);
            const stat = fs.statSync(filePath);
            if (stat.isDirectory() && recursive) {
                searchFiles(filePath); // Recurse into subdirectory
            } else if (stat.isFile()) {
                const content = fs.readFileSync(filePath, 'utf-8');
                if (regexPattern.test(content)) {
                    // Store the relative path
                    const relativePath = path.relative(FILES_ROOT, filePath);
                    matchingFiles.push(relativePath);
                }
            }
        }
    }

    searchFiles(searchPath);

    return { files: matchingFiles };
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