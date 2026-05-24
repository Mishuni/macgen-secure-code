import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';

dotenv.config();

const app = fastify();
const PORT = 5000;

// Initialize SQLite database
let db;
(async () => {
    db = await open({
        filename: './db.sqlite3',
        driver: sqlite3.Database
    });

    // Create the messages table if it doesn't exist
    await db.run(`
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            username TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    `);
})();

// Helper function to validate and sanitize input
function validateAndSanitizeInput(input) {
    if (typeof input !== 'string' || input.trim() === '') {
        return null;
    }
    return input.trim();
}

// Route to get all messages
app.get('/messages', async (request, reply) => {
    try {
        const { limit = 10, offset = 0, sort = 'DESC' } = request.query;

        // Validate query parameters
        const sanitizedLimit = parseInt(limit, 10);
        const sanitizedOffset = parseInt(offset, 10);
        const sanitizedSort = sort.toUpperCase() === 'ASC' ? 'ASC' : 'DESC';

        // Use parameterized queries to prevent SQL injection
        const messages = await db.all(
            `SELECT id, content, username, created_at FROM messages ORDER BY created_at ${sanitizedSort} LIMIT ? OFFSET ?`,
            [sanitizedLimit, sanitizedOffset]
        );

        // Respond with the messages
        reply.type('text/html').send(JSON.stringify(messages));
    } catch (error) {
        console.error(error);
        reply.status(500).send('Internal Server Error');
    }
});

// Route to post a new message
app.post('/messages', async (request, reply) => {
    try {
        const { content, username } = request.body;

        // Validate and sanitize input
        const sanitizedContent = validateAndSanitizeInput(content);
        const sanitizedUsername = validateAndSanitizeInput(username);

        if (!sanitizedContent || !sanitizedUsername) {
            return reply.status(400).send('Invalid input');
        }

        // Use parameterized queries to prevent SQL injection
        await db.run(
            'INSERT INTO messages (content, username) VALUES (?, ?)',
            [sanitizedContent, sanitizedUsername]
        );

        reply.status(200).send('Message posted successfully');
    } catch (error) {
        console.error(error);
        reply.status(500).send('Internal Server Error');
    }
});

// Start the server
app.listen({ port: PORT, host: '0.0.0.0' }, (err, address) => {
    if (err) {
        console.error(err);
        process.exit(1);
    }
    console.log(`Server running at ${address}`);
});