const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const path = require('path');

// Initialize SQLite database
async function initDb() {
    const db = await open({
        filename: path.join(__dirname, 'db.sqlite3'),
        driver: sqlite3.Database
    });

    await db.exec(`CREATE TABLE IF NOT EXISTS entries (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        lastModifiedBy TEXT,
        lastModifiedAt TEXT
    )`);

    return db;
}

// Initialize Fastify server
const start = async () => {
    const db = await initDb();

    fastify.get('/entries', async (request, reply) => {
        try {
            const entries = await db.all('SELECT id, title FROM entries');
            reply.type('text/html').send(entries.map(entry => `<div><a href="/entries/${entry.id}">${entry.title}</a></div>`).join(''));
        } catch (error) {
            reply.status(500).send('Error retrieving entries');
        }
    });

    fastify.post('/entries', async (request, reply) => {
        const { title, content, createdBy } = request.body;
        const id = require('uuid').v4();
        try {
            await db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', [id, title, content, createdBy, new Date().toISOString()]);
            reply.status(201).send({ id, title, content, lastModifiedBy: createdBy, lastModifiedAt: new Date().toISOString() });
        } catch (error) {
            reply.status(500).send('Error creating entry');
        }
    });

    fastify.get('/entries/:entryId', async (request, reply) => {
        const { entryId } = request.params;
        try {
            const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);
            if (entry) {
                reply.type('text/html').send(`<h1>${entry.title}</h1><p>${entry.content}</p><p>Last modified by: ${entry.lastModifiedBy} at ${entry.lastModifiedAt}</p>`);
            } else {
                reply.status(404).send('Entry not found');
            }
        } catch (error) {
            reply.status(500).send('Error retrieving entry');
        }
    });

    fastify.put('/entries/:entryId', async (request, reply) => {
        const { entryId } = request.params;
        const { content, modifiedBy } = request.body;
        try {
            const result = await db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', [content, modifiedBy, new Date().toISOString(), entryId]);
            if (result.changes) {
                reply.send({ message: 'Entry updated successfully' });
            } else {
                reply.status(404).send('Entry not found');
            }
        } catch (error) {
            reply.status(500).send('Error updating entry');
        }
    });

    fastify.get('/entries/:entryId/edits', async (request, reply) => {
        const { entryId } = request.params;
        // Placeholder for edit history, as no edit history is implemented in this example
        reply.status(404).send('Entry not found');
    });

    // Start server
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
};

start().catch(err => {
    fastify.log.error(err);
    process.exit(1);
});