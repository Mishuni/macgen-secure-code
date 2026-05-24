import fastify from 'fastify';
import fs from 'fs';
import path from 'path';

const app = fastify();

// Helper function to validate and sanitize input
function sanitizeInput(input) {
    if (typeof input !== 'string' || input.includes('..') || input.includes('\0')) {
        return null;
    }
    return input;
}

// Helper function to search files
function searchFiles(baseDir, searchDir, searchContent, searchFilename) {
    const results = [];
    const fullSearchDir = path.join(baseDir, searchDir || '');

    if (!fs.existsSync(fullSearchDir) || !fs.statSync(fullSearchDir).isDirectory()) {
        return results;
    }

    const files = fs.readdirSync(fullSearchDir, { withFileTypes: true });

    for (const file of files) {
        const filePath = path.join(fullSearchDir, file.name);

        if (file.isDirectory()) {
            results.push(...searchFiles(baseDir, path.join(searchDir || '', file.name), searchContent, searchFilename));
        } else if (file.isFile()) {
            if (searchFilename && file.name.includes(searchFilename)) {
                results.push(filePath);
            } else if (searchContent) {
                try {
                    const fileContent = fs.readFileSync(filePath, 'utf8');
                    if (fileContent.includes(searchContent)) {
                        results.push(filePath);
                    }
                } catch (err) {
                    // Skip files that cannot be read
                }
            }
        }
    }

    return results;
}

// Define the /search endpoint
app.post('/search', async (request, reply) => {
    const { search_content, search_filename, search_dir } = request.body;

    // Validate and sanitize inputs
    const sanitizedSearchDir = sanitizeInput(search_dir);
    const sanitizedSearchContent = typeof search_content === 'string' ? search_content : null;
    const sanitizedSearchFilename = typeof search_filename === 'string' ? search_filename : null;

    if (sanitizedSearchDir === null) {
        return reply.status(400).send({ error: 'Invalid input: search_dir' });
    }

    const baseDir = path.resolve('/data');
    const results = searchFiles(baseDir, sanitizedSearchDir, sanitizedSearchContent, sanitizedSearchFilename);

    return reply.status(200).send({ files: results });
});

// Start the server
const start = async () => {
    try {
        await app.listen({ port: 5000, host: '0.0.0.0' });
        console.log('Server is running on http://0.0.0.0:5000');
    } catch (err) {
        app.log.error(err);
        process.exit(1);
    }
};

start();