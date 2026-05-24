const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

// Open the SQLite database
async function openDb() {
    return open({
        filename: 'db.sqlite3',
        driver: sqlite3.Database
    });
}

// Initialize the database and create the necessary tables
async function initDb() {
    const db = await openDb();
    await db.exec(`
        CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            lastModifiedBy TEXT,
            lastModifiedAt TEXT
        )
    `);
    await db.close();
}

// Get all entries
fastify.get('/entries', async (request, reply) => {
    const db = await openDb();
    const entries = await db.all('SELECT id, title FROM entries');
    await db.close();
    reply.type('text/html').send(entries);
});

// Create a new entry
fastify.post('/entries', async (request, reply) => {
    const { title, content, createdBy } = request.body;
    const id = require('uuid').v4();
    const lastModifiedAt = new Date().toISOString();

    const db = await openDb();
    await db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', [id, title, content, createdBy, lastModifiedAt]);
    await db.close();

    reply.code(201).send({ id, title, content, lastModifiedBy: createdBy, lastModifiedAt });
});

// Get a specific entry
fastify.get('/entries/:entryId', async (request, reply) => {
    const { entryId } = request.params;
    const db = await openDb();
    const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);
    await db.close();

    if (!entry) {
        return reply.code(404).send({ message: 'Entry not found' });
    }

    reply.type('text/html').send(entry);
});

// Update an existing entry
fastify.put('/entries/:entryId', async (request, reply) => {
    const { entryId } = request.params;
    const { content, modifiedBy, summary } = request.body;
    const lastModifiedAt = new Date().toISOString();

    const db = await openDb();
    const result = await db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', [content, modifiedBy, lastModifiedAt, entryId]);
    await db.close();

    if (result.changes === 0) {
        return reply.code(404).send({ message: 'Entry not found' });
    }

    reply.send({ message: 'Entry updated successfully' });
});

// View the history of edits for a specific entry (dummy implementation)
fastify.get('/entries/:entryId/edits', async (request, reply) => {
    const { entryId } = request.params;
    // In a real implementation, you would fetch edit history from a separate table
    const db = await openDb();
    const edits = await db.all('SELECT * FROM entries WHERE id = ?', [entryId]); // Placeholder for edit history
    await db.close();

    if (!edits.length) {
        return reply.code(404).send({ message: 'Entry not found' });
    }

    reply.type('text/html').send(edits);
});

// Start the server
const start = async () => {
    await initDb();
    try {
        await fastify.listen({ port: 5000, host: '0.0.0.0' });
        fastify.log.info(`Server listening on http://0.0.0.0:5000`);
    } catch (err) {
        fastify.log.error(err);
        process.exit(1);
    }
};

start();