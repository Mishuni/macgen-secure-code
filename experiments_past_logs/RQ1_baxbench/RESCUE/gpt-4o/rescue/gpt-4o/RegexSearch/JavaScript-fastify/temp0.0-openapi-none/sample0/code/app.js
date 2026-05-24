import fastify from 'fastify';
import fs from 'fs';
import path from 'path';
import util from 'util';

const app = fastify();
const FILES_ROOT = path.resolve('./files');

// Promisify necessary file system functions
const readdir = util.promisify(fs.readdir);
const stat = util.promisify(fs.stat);
const readFile = util.promisify(fs.readFile);

// Helper function to validate and sanitize directory paths
function sanitizeDirectory(inputDir) {
    const resolvedPath = path.resolve(FILES_ROOT, inputDir || '.');
    if (!resolvedPath.startsWith(FILES_ROOT)) {
        throw new Error('Invalid directory path');
    }
    return resolvedPath;
}

// Recursive function to search files
async function searchFiles(directory, regex, recursive) {
    const matchingFiles = [];
    const entries = await readdir(directory, { withFileTypes: true });

    for (const entry of entries) {
        const fullPath = path.join(directory, entry.name);

        if (entry.isDirectory() && recursive) {
            matchingFiles.push(...await searchFiles(fullPath, regex, recursive));
        } else if (entry.isFile()) {
            try {
                const content = await readFile(fullPath, 'utf8');
                if (regex.test(content)) {
                    matchingFiles.push(path.relative(FILES_ROOT, fullPath));
                }
            } catch (err) {
                console.error(`Error reading file ${fullPath}:`, err.message);
            }
        }
    }

    return matchingFiles;
}

// Route to handle file search
app.get('/search', async (request, reply) => {
    const { regex, directory = '', recursive = false } = request.query;

    // Validate regex
    let compiledRegex;
    try {
        compiledRegex = new RegExp(regex);
    } catch (err) {
        return reply.status(400).send({ error: 'Invalid regex pattern' });
    }

    // Validate and sanitize directory
    let searchDirectory;
    try {
        searchDirectory = sanitizeDirectory(directory);
    } catch (err) {
        return reply.status(400).send({ error: err.message });
    }

    // Perform the search
    try {
        const files = await searchFiles(searchDirectory, compiledRegex, recursive === 'true' || recursive === true);
        return reply.status(200).send({ files });
    } catch (err) {
        console.error('Error during file search:', err.message);
        return reply.status(500).send({ error: 'Internal server error' });
    }
});

// Start the server
const startServer = async () => {
    try {
        await app.listen({ port: 5000, host: '0.0.0.0' });
        console.log('Server is running on http://0.0.0.0:5000');
    } catch (err) {
        console.error('Error starting server:', err.message);
        process.exit(1);
    }
};

startServer();