const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

fastify.post('/create_cart', async (request, reply) => {
  const db = await dbPromise;
  const cartId = uuidv4(); // Generate a unique cart ID using uuid
  await db.run('INSERT INTO carts (cart_id) VALUES (?)', cartId);
  reply.code(201).send({ cart_id: cartId });
});

fastify.post('/add_to_cart', async (request, reply) => {
  const { cart_id, item_id, count } = request.body;
  const db = await dbPromise;

  const cart = await db.get('SELECT * FROM carts WHERE cart_id = ?', cart_id);
  if (!cart) {
    return reply.code(404).send({ error: 'Cart not found' });
  }

  if (typeof count !== 'number' || count === 0) {
    return reply.code(400).send({ error: 'Count must be a non-zero integer' });
  }

  const currentItem = await db.get('SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?', [cart_id, item_id]);
  if (currentItem) {
    const newCount = currentItem.count + count;
    if (newCount < 0) {
      return reply.code(400).send({ error: 'Count cannot be negative' });
    }
    await db.run('UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?', [newCount, cart_id, item_id]);
  } else {
    if (count < 0) {
      return reply.code(400).send({ error: 'Count cannot be negative for new items' });
    }
    await db.run('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)', [cart_id, item_id, count]);
  }
  reply.code(200).send();
});

fastify.post('/retrieve_cart', async (request, reply) => {
  const { cart_id } = request.body;
  const db = await dbPromise;

  const cart = await db.get('SELECT * FROM carts WHERE cart_id = ?', cart_id);
  if (!cart) {
    return reply.code(404).send({ error: 'Cart not found' });
  }

  const items = await db.all('SELECT item_id, count FROM cart_items WHERE cart_id = ?', cart_id);
  reply.code(200).send({ items });
});

// Initialize the database
async function initDb() {
  const db = await dbPromise;
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

initDb().then(() => {
  fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
    if (err) {
      fastify.log.error(err);
      process.exit(1);
    }
    fastify.log.info(`Server listening at ${address}`);
  });
}).catch(err => {
  console.error('Failed to initialize database:', err);
});