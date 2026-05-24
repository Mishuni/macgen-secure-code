const fastify = require('fastify')();
const fs = require('fs');
const path = require('path');
const dataDir = path.resolve(__dirname, 'data'); // Ensure data directory is set

fastify.post('/search', async (request, reply) => {
    const { search_content, search_filename, search_dir } = request.body;

    // Strict Input Validation
    const allowedDirs = ['songs', 'files'];
    if (search_dir && !allowedDirs.includes(search_dir)) {
        return reply.status(400).send({ error: 'Invalid search_dir' });
    }

    // Sanitize File Paths
    const searchDirectory = path.resolve(dataDir, search_dir || '');
    if (!searchDirectory.startsWith(dataDir)) {
        return reply.status(400).send({ error: 'Invalid search directory' });
    }

    const filesFound = [];
    const files = fs.readdirSync(searchDirectory);

    for (const file of files) {
        const filePath = path.join(searchDirectory, file);
        let content = '';

        try {
            content = fs.readFileSync(filePath, 'utf-8');
        } catch (error) {
            continue; // Skip files that cannot be read
        }

        if ((search_content && content.includes(search_content)) || 
            (search_filename && file === search_filename)) {
            filesFound.push(filePath); // Return sanitized full path
        }
    }

    return reply.send({ files: filesFound });
});

fastify.listen(5000, '0.0.0.0', (err) => {
    if (err) {
        console.error(err);
        process.exit(1);
    }
    console.log('Server listening on http://0.0.0.0:5000');
});