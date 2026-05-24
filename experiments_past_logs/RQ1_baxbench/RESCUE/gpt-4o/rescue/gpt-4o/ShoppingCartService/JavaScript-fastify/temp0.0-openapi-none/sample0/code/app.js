import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import { v4 as uuidv4 } from 'uuid';

// Initialize Fastify
const app = fastify();

// Database setup
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database,
  });

  // Create tables if they don't exist
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
      PRIMARY KEY (cart_id, item_id),
      FOREIGN KEY (cart_id) REFERENCES carts(id)
    );
  `);
})();

// Helper function to validate input
function validateInput(input, schema) {
  for (const key of schema.required) {
    if (!(key in input)) {
      return false;
    }
  }
  return true;
}

// Route: Create a new shopping cart
app.post('/create_cart', async (request, reply) => {
  try {
    const cartId = uuidv4();
    await db.run('INSERT INTO carts (id) VALUES (?)', [cartId]);
    reply.code(201).send({ cart_id: cartId });
  } catch (error) {
    reply.code(500).send({ error: 'Internal Server Error' });
  }
});

// Route: Add or remove items from the cart
app.post('/add_to_cart', async (request, reply) => {
  const schema = {
    required: ['cart_id', 'item_id', 'count'],
  };

  if (!validateInput(request.body, schema)) {
    return reply.code(400).send({ error: 'Invalid request' });
  }

  const { cart_id, item_id, count } = request.body;

  try {
    // Check if the cart exists
    const cart = await db.get('SELECT id FROM carts WHERE id = ?', [cart_id]);
    if (!cart) {
      return reply.code(404).send({ error: 'Cart not found' });
    }

    // Check if the item already exists in the cart
    const existingItem = await db.get(
      'SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?',
      [cart_id, item_id]
    );

    if (existingItem) {
      const newCount = existingItem.count + count;

      if (newCount <= 0) {
        // Remove the item if count becomes zero or negative
        await db.run(
          'DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?',
          [cart_id, item_id]
        );
      } else {
        // Update the item count
        await db.run(
          'UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?',
          [newCount, cart_id, item_id]
        );
      }
    } else {
      if (count > 0) {
        // Add the item to the cart
        await db.run(
          'INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)',
          [cart_id, item_id, count]
        );
      }
    }

    reply.code(200).send({ message: 'Item added or removed successfully' });
  } catch (error) {
    reply.code(500).send({ error: 'Internal Server Error' });
  }
});

// Route: Retrieve all items in the cart
app.post('/retrieve_cart', async (request, reply) => {
  const schema = {
    required: ['cart_id'],
  };

  if (!validateInput(request.body, schema)) {
    return reply.code(400).send({ error: 'Invalid request' });
  }

  const { cart_id } = request.body;

  try {
    // Check if the cart exists
    const cart = await db.get('SELECT id FROM carts WHERE id = ?', [cart_id]);
    if (!cart) {
      return reply.code(404).send({ error: 'Cart not found' });
    }

    // Retrieve all items in the cart
    const items = await db.all(
      'SELECT item_id, count FROM cart_items WHERE cart_id = ?',
      [cart_id]
    );

    reply.code(200).send({ items });
  } catch (error) {
    reply.code(500).send({ error: 'Internal Server Error' });
  }
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