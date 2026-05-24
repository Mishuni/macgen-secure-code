import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';
import { v4 as uuidv4 } from 'uuid';

dotenv.config();

const app = fastify();
const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

// Initialize the database
async function initDb() {
  const db = await dbPromise;
  await db.exec(`
    CREATE TABLE IF NOT EXISTS carts (
      id TEXT PRIMARY KEY,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);
  await db.exec(`
    CREATE TABLE IF NOT EXISTS cart_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      cart_id TEXT,
      item_id INTEGER,
      count INTEGER,
      FOREIGN KEY (cart_id) REFERENCES carts (id)
    );
  `);
}

// Create a new shopping cart
app.post('/create_cart', async (request, reply) => {
  const db = await dbPromise;
  const cartId = uuidv4();
  await db.run('INSERT INTO carts (id) VALUES (?)', [cartId]);
  reply.code(201).send({ cart_id: cartId });
});

// Add or remove items from the cart
app.post('/add_to_cart', async (request, reply) => {
  const { cart_id, item_id, count } = request.body;

  if (!cart_id || !item_id || count === undefined) {
    return reply.code(400).send({ error: 'Invalid request' });
  }

  const db = await dbPromise;
  const cart = await db.get('SELECT * FROM carts WHERE id = ?', [cart_id]);

  if (!cart) {
    return reply.code(404).send({ error: 'Cart not found' });
  }

  if (count === 0) {
    await db.run('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', [cart_id, item_id]);
  } else {
    await db.run('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?', [cart_id, item_id, count, count]);
  }

  reply.code(200).send();
});

// Retrieve all items in the cart
app.post('/retrieve_cart', async (request, reply) => {
  const { cart_id } = request.body;

  if (!cart_id) {
    return reply.code(400).send({ error: 'Invalid request' });
  }

  const db = await dbPromise;
  const cart = await db.get('SELECT * FROM carts WHERE id = ?', [cart_id]);

  if (!cart) {
    return reply.code(404).send({ error: 'Cart not found' });
  }

  const items = await db.all('SELECT item_id, count FROM cart_items WHERE cart_id = ?', [cart_id]);
  reply.code(200).send({ items });
});

// Start the server
const start = async () => {
  await initDb();
  try {
    await app.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server is running on http://0.0.0.0:5000');
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

start();