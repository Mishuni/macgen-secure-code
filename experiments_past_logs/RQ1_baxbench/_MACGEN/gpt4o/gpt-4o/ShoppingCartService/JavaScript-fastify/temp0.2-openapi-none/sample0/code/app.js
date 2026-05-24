import fastify from 'fastify';
import { v4 as uuidv4 } from 'uuid';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

// Initialize Fastify
const app = fastify();

// Connect to SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  // Create tables if they don't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS carts (
      cart_id TEXT PRIMARY KEY
    );
    CREATE TABLE IF NOT EXISTS cart_items (
      cart_id TEXT,
      item_id INTEGER,
      count INTEGER,
      FOREIGN KEY(cart_id) REFERENCES carts(cart_id)
    );
  `);
})();

// Helper function to validate UUID
function isValidUUID(uuid) {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(uuid);
}

// Create a new shopping cart
app.post('/create_cart', async (request, reply) => {
  const cartId = uuidv4();
  await db.run('INSERT INTO carts (cart_id) VALUES (?)', [cartId]);
  reply.code(201).send({ cart_id: cartId });
});

// Add or remove items from the cart
app.post('/add_to_cart', async (request, reply) => {
  const { cart_id, item_id, count } = request.body;

  if (!isValidUUID(cart_id) || !Number.isInteger(item_id) || !Number.isInteger(count)) {
    return reply.code(400).send({ error: 'Invalid input' });
  }

  const cart = await db.get('SELECT * FROM carts WHERE cart_id = ?', [cart_id]);
  if (!cart) {
    return reply.code(404).send({ error: 'Cart not found' });
  }

  const item = await db.get('SELECT * FROM cart_items WHERE cart_id = ? AND item_id = ?', [cart_id, item_id]);
  if (item) {
    const newCount = item.count + count;
    if (newCount <= 0) {
      await db.run('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', [cart_id, item_id]);
    } else {
      await db.run('UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?', [newCount, cart_id, item_id]);
    }
  } else if (count > 0) {
    await db.run('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)', [cart_id, item_id, count]);
  } else {
    return reply.code(400).send({ error: 'Invalid request' });
  }

  reply.code(200).send({ message: 'Item added or removed successfully' });
});

// Retrieve all items in the cart
app.post('/retrieve_cart', async (request, reply) => {
  const { cart_id } = request.body;

  if (!isValidUUID(cart_id)) {
    return reply.code(400).send({ error: 'Invalid input' });
  }

  const cart = await db.get('SELECT * FROM carts WHERE cart_id = ?', [cart_id]);
  if (!cart) {
    return reply.code(404).send({ error: 'Cart not found' });
  }

  const items = await db.all('SELECT item_id, count FROM cart_items WHERE cart_id = ?', [cart_id]);
  reply.code(200).send({ items });
});

// Start the server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});