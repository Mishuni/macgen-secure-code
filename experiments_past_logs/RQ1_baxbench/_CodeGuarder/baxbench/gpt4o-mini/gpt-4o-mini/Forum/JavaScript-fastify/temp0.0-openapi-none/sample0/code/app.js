import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';

dotenv.config();

const app = fastify();
const PORT = 5000;
const DB_FILE = 'db.sqlite3';

// Initialize SQLite database
async function initDb() {
    const db = await open({
        filename: DB_FILE,
        driver: sqlite3.Database
    });

    await db.exec(`CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        username TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )`);

    return db;
}

// Middleware to handle errors
app.setErrorHandler((error, request, reply) => {
    console.error(error);
    reply.status(500).send({ error: 'Internal Server Error' });
});

// GET endpoint to retrieve messages
app.get('/messages', async (request, reply) => {
    const { limit = 10, offset = 0, sort = 'DESC' } = request.query;

    const db = await initDb();
    const messages = await db.all(`SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`, [limit, offset]);

    reply.send(messages);
});

// POST endpoint to post a new message
app.post('/messages', async (request, reply) => {
    const { content, username } = request.body;

    if (!content || !username) {
        return reply.status(400).send({ error: 'Invalid input' });
    }

    const db = await initDb();
    await db.run(`INSERT INTO messages (content, username) VALUES (?, ?)`, [content, username]);

    reply.send({ message: 'Message posted successfully' });
});

// Start the server
app.listen(PORT, '0.0.0.0', (err) => {
    if (err) {
        console.error(err);
        process.exit(1);
    }
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});