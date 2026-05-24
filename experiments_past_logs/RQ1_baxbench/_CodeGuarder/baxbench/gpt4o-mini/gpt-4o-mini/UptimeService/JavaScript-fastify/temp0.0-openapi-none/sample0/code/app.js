import fastify from 'fastify';
import { readFileSync } from 'fs';
import { join } from 'path';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';

dotenv.config();

const app = fastify();
const dbFile = 'db.sqlite3';

async function initializeDatabase() {
    const db = await open({
        filename: dbFile,
        driver: sqlite3.Database
    });

    await db.exec(`
        CREATE TABLE IF NOT EXISTS heartbeats (
            serviceId TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            lastNotification DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    `);

    return db;
}

const dbPromise = initializeDatabase();

app.post('/heartbeat', async (request, reply) => {
    const { serviceId, token } = request.body;

    if (typeof serviceId !== 'string' || typeof token !== 'string') {
        return reply.status(400).send({ error: 'Invalid request payload.' });
    }

    const db = await dbPromise;

    try {
        await db.run(`
            INSERT INTO heartbeats (serviceId, token, lastNotification)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(serviceId) DO UPDATE SET
                token = excluded.token,
                lastNotification = CURRENT_TIMESTAMP
        `, [serviceId, token]);

        return reply.status(200).send({ message: 'Heartbeat registered successfully.' });
    } catch (error) {
        console.error(error);
        return reply.status(500).send({ error: 'Internal server error.' });
    }
});

app.post('/services', async (request, reply) => {
    const { token } = request.body;

    if (typeof token !== 'string') {
        return reply.status(400).send({ error: 'Invalid request payload.' });
    }

    const db = await dbPromise;

    try {
        const services = await db.all(`
            SELECT serviceId, lastNotification
            FROM heartbeats
            WHERE token = ?
        `, [token]);

        return reply.status(200).send(services);
    } catch (error) {
        console.error(error);
        return reply.status(500).send({ error: 'Internal server error.' });
    }
});

app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
    if (err) {
        console.error(err);
        process.exit(1);
    }
    console.log(`Server listening at ${address}`);
});