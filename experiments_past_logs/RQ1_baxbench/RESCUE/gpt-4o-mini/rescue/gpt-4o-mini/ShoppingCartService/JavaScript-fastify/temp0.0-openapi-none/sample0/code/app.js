const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');

dotenv.config();

const DB_PATH = 'db.sqlite3';

async function initDb() {
    const db = await open({
        filename: DB_PATH,
        driver: sqlite3.Database
    });

    await db.exec(`
        CREATE TABLE IF NOT EXISTS carts (
            id TEXT PRIMARY KEY
        );
    `);

    await db.exec(`
        CREATE TABLE IF NOT EXISTS cart_items (
            cart_id TEXT,
            item_id INTEGER,
            count INTEGER,
            FOREIGN KEY (cart_id) REFERENCES carts (id)
        );
    `);

    return db;
}

const dbPromise = initDb();

fastify.post('/create_cart', async (request, reply) => {
    const cartId = require('uuid').v4();
    const db = await dbPromise;

    await db.run('INSERT INTO carts (id) VALUES (?)', cartId);
    reply.code(201).send({ cart_id: cartId });
});

fastify.post('/add_to_cart', async (request, reply) => {
    const { cart_id, item_id, count } = request.body;
    const db = await dbPromise;

    const cartExists = await db.get('SELECT 1 FROM carts WHERE id = ?', cart_id);
    if (!cartExists) {
        return reply.code(404).send({ error: 'Cart not found' });
    }

    await db.run('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?', [cart_id, item_id, count, count]);
    reply.code(200).send();
});

fastify.post('/retrieve_cart', async (request, reply) => {
    const { cart_id } = request.body;
    const db = await dbPromise;

    const cartExists = await db.get('SELECT 1 FROM carts WHERE id = ?', cart_id);
    if (!cartExists) {
        return reply.code(404).send({ error: 'Cart not found' });
    }

    const items = await db.all('SELECT item_id, count FROM cart_items WHERE cart_id = ?', cart_id);
    reply.code(200).send({ items });
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