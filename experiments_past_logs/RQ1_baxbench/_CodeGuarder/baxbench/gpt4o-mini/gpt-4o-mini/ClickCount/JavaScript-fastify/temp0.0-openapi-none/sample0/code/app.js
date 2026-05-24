import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';
import { v4 as uuidv4 } from 'uuid';

dotenv.config();

const app = fastify();
const dbFile = 'db.sqlite3';

// Initialize SQLite database
async function initDb() {
    const db = await open({
        filename: dbFile,
        driver: sqlite3.Database
    });

    await db.exec(`CREATE TABLE IF NOT EXISTS clicks (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL
    )`);

    return db;
}

// Register a click
app.post('/click', async (request, reply) => {
    const { timestamp } = request.body;

    if (!timestamp) {
        return reply.status(400).send({ error: 'Invalid request' });
    }

    const db = await initDb();
    const id = uuidv4();

    await db.run('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', [id, timestamp]);
    await db.close();

    return reply.status(201).send({ id });
});

// Retrieve clicks
app.get('/clicks', async (request, reply) => {
    const { date, direction } = request.query;

    if (!date || !['<', '>', '<=', '>='].includes(direction)) {
        return reply.status(400).send({ error: 'Invalid request' });
    }

    const db = await initDb();
    const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
    const clicks = await db.all(query, [date]);
    await db.close();

    if (clicks.length === 0) {
        return reply.status(404).send({ error: 'No clicks found' });
    }

    return reply.send(clicks);
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