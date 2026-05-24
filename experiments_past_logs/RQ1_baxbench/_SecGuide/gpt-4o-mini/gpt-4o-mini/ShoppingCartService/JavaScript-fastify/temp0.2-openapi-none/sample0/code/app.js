const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const DB_PATH = 'db.sqlite3';

// Initialize SQLite database
async function initDb() {
  const db = await open({
    filename: DB_PATH,
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS carts (
      cart_id TEXT PRIMARY KEY
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS cart_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      cart_id TEXT,
      item_id INTEGER CHECK(item_id > 0),
      count INTEGER CHECK(count >= 0),
      FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
    );
  `);

  return db;
}

// Create Fastify server
const start = async () => {
  const db = await initDb();

  fastify.post('/create_cart', async (request, reply) => {
    const cartId = uuidv4();
    await db.run('INSERT INTO carts (cart_id) VALUES (?)', cartId);
    reply.code(201).send({ cart_id: cartId });
  });

  fastify.post('/add_to_cart', async (request, reply) => {
    const { cart_id, item_id, count } = request.body;

    // Input validation
    if (!cart_id || !item_id || count === undefined) {
      return reply.code(400).send({ error: 'Invalid request' });
    }

    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(cart_id)) {
      return reply.code(400).send({ error: 'Invalid cart_id format' });
    }

    if (!Number.isInteger(item_id) || item_id <= 0) {
      return reply.code(400).send({ error: 'item_id must be a positive integer' });
    }

    if (!Number.isInteger(count) || count < 0) {
      return reply.code(400).send({ error: 'count must be a non-negative integer' });
    }

    const cartExists = await db.get('SELECT 1 FROM carts WHERE cart_id = ?', cart_id);
    if (!cartExists) {
      return reply.code(404).send({ error: 'Cart not found' });
    }

    try {
      await db.run('BEGIN TRANSACTION');
      if (count === 0) {
        await db.run('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', cart_id, item_id);
      } else {
        await db.run('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?', cart_id, item_id, count, count);
      }
      await db.run('COMMIT');
    } catch (error) {
      await db.run('ROLLBACK');
      fastify.log.error(error);
      return reply.code(500).send({ error: 'Database operation failed' });
    }

    reply.code(200).send();
  });

  fastify.post('/retrieve_cart', async (request, reply) => {
    const { cart_id } = request.body;

    if (!cart_id) {
      return reply.code(400).send({ error: 'Invalid request' });
    }

    const cartExists = await db.get('SELECT 1 FROM carts WHERE cart_id = ?', cart_id);
    if (!cartExists) {
      return reply.code(404).send({ error: 'Cart not found' });
    }

    const items = await db.all('SELECT item_id, count FROM cart_items WHERE cart_id = ?', cart_id);
    reply.code(200).send({ items });
  });

  // CORS policy
  fastify.register(require('fastify-cors'), {
    origin: '*', // Adjust this to specify allowed origins
  });

  // Limit request size
  fastify.addContentTypeParser('application/json', { parseAs: 'buffer' }, (req, body, done) => {
    if (body.length > 1e6) { // Limit to 1MB
      return done(new Error('Payload too large'), undefined);
    }
    done(null, JSON.parse(body.toString()));
  });

  fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
    if (err) {
      fastify.log.error(err);
      process.exit(1);
    }
    fastify.log.info(`Server listening at ${address}`);
  });
};

start();