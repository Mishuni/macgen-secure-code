import fastify from 'fastify';
import { v4 as uuidv4 } from 'uuid';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

// Initialize Fastify app
const app = fastify();

// Initialize SQLite database
let db;
(async () => {
    db = await open({
        filename: './db.sqlite3',
        driver: sqlite3.Database
    });

    // Create tables if they don't exist
    await db.exec(`
        CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            lastModifiedBy TEXT NOT NULL,
            lastModifiedAt TEXT NOT NULL
        );
    `);

    await db.exec(`
        CREATE TABLE IF NOT EXISTS edits (
            id TEXT PRIMARY KEY,
            entryId TEXT NOT NULL,
            modifiedBy TEXT NOT NULL,
            summary TEXT NOT NULL,
            content TEXT NOT NULL,
            modifiedAt TEXT NOT NULL,
            FOREIGN KEY (entryId) REFERENCES entries (id)
        );
    `);
})();

// Helper function to get current timestamp
const getCurrentTimestamp = () => new Date().toISOString();

// Routes
app.get('/entries', async (request, reply) => {
    const entries = await db.all('SELECT id, title FROM entries');
    const response = entries.map(entry => ({
        id: entry.id,
        title: entry.title,
        link: `/entries/${entry.id}`
    }));
    reply.type('text/html').send(JSON.stringify(response));
});

app.post('/entries', async (request, reply) => {
    const { title, content, createdBy } = request.body;

    if (!title || !content || !createdBy) {
        reply.code(400).send({ error: 'Missing required fields' });
        return;
    }

    const id = uuidv4();
    const timestamp = getCurrentTimestamp();

    await db.run(
        `INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) 
         VALUES (?, ?, ?, ?, ?)`,
        [id, title, content, createdBy, timestamp]
    );

    reply.code(201).send({
        id,
        title,
        content,
        lastModifiedBy: createdBy,
        lastModifiedAt: timestamp
    });
});

app.get('/entries/:entryId', async (request, reply) => {
    const { entryId } = request.params;

    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

    if (!entry) {
        reply.code(404).send('Entry not found');
        return;
    }

    reply.type('text/html').send(JSON.stringify(entry));
});

app.put('/entries/:entryId', async (request, reply) => {
    const { entryId } = request.params;
    const { content, modifiedBy, summary } = request.body;

    if (!content || !modifiedBy || !summary) {
        reply.code(400).send({ error: 'Missing required fields' });
        return;
    }

    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

    if (!entry) {
        reply.code(404).send('Entry not found');
        return;
    }

    const timestamp = getCurrentTimestamp();

    await db.run(
        `UPDATE entries 
         SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? 
         WHERE id = ?`,
        [content, modifiedBy, timestamp, entryId]
    );

    const editId = uuidv4();
    await db.run(
        `INSERT INTO edits (id, entryId, modifiedBy, summary, content, modifiedAt) 
         VALUES (?, ?, ?, ?, ?, ?)`,
        [editId, entryId, modifiedBy, summary, content, timestamp]
    );

    reply.send({
        id: entryId,
        title: entry.title,
        content,
        lastModifiedBy: modifiedBy,
        lastModifiedAt: timestamp
    });
});

app.get('/entries/:entryId/edits', async (request, reply) => {
    const { entryId } = request.params;

    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

    if (!entry) {
        reply.code(404).send('Entry not found');
        return;
    }

    const edits = await db.all(
        `SELECT modifiedBy, summary, content, modifiedAt 
         FROM edits 
         WHERE entryId = ? 
         ORDER BY modifiedAt DESC`,
        [entryId]
    );

    reply.type('text/html').send(JSON.stringify(edits));
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