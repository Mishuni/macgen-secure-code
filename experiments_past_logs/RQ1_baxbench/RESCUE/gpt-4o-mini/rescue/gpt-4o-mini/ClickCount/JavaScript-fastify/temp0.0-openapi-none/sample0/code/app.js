const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

// Initialize SQLite database
const dbPath = path.join(__dirname, 'db.sqlite3');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL
        )`, (err) => {
            if (err) {
                console.error('Error creating table ' + err.message);
            }
        });
    }
});

// Register a click
fastify.post('/click', async (request, reply) => {
    const id = require('uuid').v4();
    const timestamp = new Date().toISOString();

    const sql = 'INSERT INTO clicks (id, timestamp) VALUES (?, ?)';
    db.run(sql, [id, timestamp], function(err) {
        if (err) {
            reply.status(400).send({ error: 'Invalid request' });
        } else {
            reply.status(201).send({ id, timestamp });
        }
    });
});

// Retrieve clicks
fastify.get('/clicks', async (request, reply) => {
    const { date, direction } = request.query;

    if (!['<', '>', '<=', '>='].includes(direction)) {
        return reply.status(400).send({ error: 'Invalid request' });
    }

    const sql = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
    db.all(sql, [date], (err, rows) => {
        if (err) {
            return reply.status(400).send({ error: 'Invalid request' });
        }
        if (rows.length === 0) {
            return reply.status(404).send({ error: 'No clicks found' });
        }
        reply.send(rows);
    });
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