const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    console.error('Error opening database ' + err.message);
  } else {
    db.run(`CREATE TABLE IF NOT EXISTS carts (
            cart_id TEXT PRIMARY KEY
        )`, (err) => {
      if (err) {
        console.error('Error creating carts table ' + err.message);
      }
    });

    db.run(`CREATE TABLE IF NOT EXISTS cart_items (
            cart_id TEXT,
            item_id INTEGER,
            count INTEGER,
            PRIMARY KEY (cart_id, item_id),
            FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
        )`, (err) => {
      if (err) {
        console.error('Error creating cart_items table ' + err.message);
      }
    });
  }
});

// Create a new shopping cart
fastify.post('/create_cart', async (request, reply) => {
  const cartId = uuidv4();
  db.run(`INSERT INTO carts (cart_id) VALUES (?)`, [cartId], function (err) {
    if (err) {
      reply.status(500).send({ error: 'Failed to create cart' });
    } else {
      reply.status(201).send({ cart_id: cartId });
    }
  });
});

// Add or remove items from the cart
fastify.post('/add_to_cart', async (request, reply) => {
  const { cart_id, item_id, count } = request.body;

  if (typeof cart_id !== 'string' || typeof item_id !== 'number' || typeof count !== 'number') {
    return reply.status(400).send({ error: 'Invalid request parameters' });
  }

  db.get(`SELECT * FROM carts WHERE cart_id = ?`, [cart_id], (err, row) => {
    if (err || !row) {
      reply.status(404).send({ error: 'Cart not found' });
    } else {
      db.get(`SELECT * FROM cart_items WHERE cart_id = ? AND item_id = ?`, [cart_id, item_id], (err, itemRow) => {
        if (err) {
          reply.status(500).send({ error: 'Database error' });
        } else if (itemRow) {
          const newCount = itemRow.count + count;
          if (newCount <= 0) {
            db.run(`DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?`, [cart_id, item_id], function (err) {
              if (err) {
                reply.status(500).send({ error: 'Failed to update cart' });
              } else {
                reply.status(200).send({ message: 'Item removed successfully' });
              }
            });
          } else {
            db.run(`UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?`, [newCount, cart_id, item_id], function (err) {
              if (err) {
                reply.status(500).send({ error: 'Failed to update cart' });
              } else {
                reply.status(200).send({ message: 'Item updated successfully' });
              }
            });
          }
        } else if (count > 0) {
          db.run(`INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)`, [cart_id, item_id, count], function (err) {
            if (err) {
              reply.status(500).send({ error: 'Failed to add item to cart' });
            } else {
              reply.status(200).send({ message: 'Item added successfully' });
            }
          });
        } else {
          reply.status(400).send({ error: 'Invalid item count' });
        }
      });
    }
  });
});

// Retrieve all items in the cart
fastify.post('/retrieve_cart', async (request, reply) => {
  const { cart_id } = request.body;

  if (typeof cart_id !== 'string') {
    return reply.status(400).send({ error: 'Invalid request parameters' });
  }

  db.get(`SELECT * FROM carts WHERE cart_id = ?`, [cart_id], (err, row) => {
    if (err || !row) {
      reply.status(404).send({ error: 'Cart not found' });
    } else {
      db.all(`SELECT item_id, count FROM cart_items WHERE cart_id = ?`, [cart_id], (err, rows) => {
        if (err) {
          reply.status(500).send({ error: 'Failed to retrieve cart items' });
        } else {
          reply.status(200).send({ items: rows });
        }
      });
    }
  });
});

// Start the server
fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});