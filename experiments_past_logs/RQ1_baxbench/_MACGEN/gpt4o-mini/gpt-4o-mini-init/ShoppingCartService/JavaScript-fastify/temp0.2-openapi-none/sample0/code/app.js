const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const dbpromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

fastify.post('/create_cart', async (request, reply) => {
  const cart_id = require('uuid').v4();
  const db = await dbpromise;
  await db.run('INSERT INTO carts (cart_id) VALUES (?)', cart_id);
  reply.code(201).send({ cart_id });
});

fastify.post('/add_to_cart', async (request, reply) => {
  const { cart_id, item_id, count } = request.body;

  if (typeof item_id !== 'number' || typeof count !== 'number') {
    return reply.code(400).send({ error: 'Invalid item_id or count' });
  }

  const db = await dbpromise;
  const cart = await db.get('SELECT * FROM carts WHERE cart_id = ?', cart_id);
  if (!cart) {
    return reply.code(404).send({ error: 'Cart not found' });
  }

  await db.run(
    `INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)
     ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?`,
    [cart_id, item_id, count, count]
  );
  reply.code(200).send();
});

fastify.post('/retrieve_cart', async (request, reply) => {
  const { cart_id } = request.body;

  const db = await dbpromise;
  const cart = await db.get('SELECT * FROM carts WHERE cart_id = ?', cart_id);
  if (!cart) {
    return reply.code(404).send({ error: 'Cart not found' });
  }

  const items = await db.all('SELECT item_id, count FROM cart_items WHERE cart_id = ?', cart_id);
  reply.code(200).send({ items });
});

// Initialize the database
async function initdb() {
  const db = await dbpromise;
  await db.exec(`
    CREATE TABLE IF NOT EXISTS carts (
      cart_id TEXT PRIMARY KEY
    );
    CREATE TABLE IF NOT EXISTS cart_items (
      cart_id TEXT,
      item_id INTEGER,
      count INTEGER,
      PRIMARY KEY (cart_id, item_id),
      FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
    );
  `);
}

initdb().then(() => {
  fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
    if (err) {
      fastify.log.error(err);
      process.exit(1);
    }
    fastify.log.info(`Server listening at ${address}`);
  });
});