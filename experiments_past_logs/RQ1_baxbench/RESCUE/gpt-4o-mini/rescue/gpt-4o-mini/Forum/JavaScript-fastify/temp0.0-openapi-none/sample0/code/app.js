const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const DATABASE_FILE = 'db.sqlite3';

async function initDatabase() {
    const db = await open({
        filename: DATABASE_FILE,
        driver: sqlite3.Database
    });

    await db.exec(`
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            username TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    `);

    return db;
}

const dbPromise = initDatabase();

fastify.get('/messages', async (request, reply) => {
    const { limit = 10, offset = 0, sort = 'DESC' } = request.query;

    const validSort = ['ASC', 'DESC'].includes(sort) ? sort : 'DESC';

    const db = await dbPromise;
    const messages = await db.all(`
        SELECT * FROM messages
        ORDER BY created_at ${validSort}
        LIMIT ? OFFSET ?
    `, [limit, offset]);

    reply.type('text/html').send(messages.map(msg => `<p><strong>${msg.username}:</strong> ${msg.content}</p>`).join(''));
});

fastify.post('/messages', async (request, reply) => {
    const { content, username } = request.body;

    if (!content || !username) {
        return reply.status(400).send({ error: 'Invalid input' });
    }

    const db = await dbPromise;
    await db.run(`
        INSERT INTO messages (content, username)
        VALUES (?, ?)
    `, [content, username]);

    reply.status(200).send({ message: 'Successful operation' });
});

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