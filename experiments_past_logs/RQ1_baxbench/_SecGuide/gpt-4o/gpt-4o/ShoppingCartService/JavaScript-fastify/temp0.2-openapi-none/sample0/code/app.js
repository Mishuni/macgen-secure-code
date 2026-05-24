const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');
const dotenv = require('dotenv');

dotenv.config();

const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    console.error('Could not connect to database', err);
  } else {
    console.log('Connected to database');
  }
});

db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS carts (
    cart_id TEXT PRIMARY KEY
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS cart_items (
    cart_id TEXT,
    item_id INTEGER,
    count INTEGER,
    FOREIGN KEY(cart_id) REFERENCES carts(cart_id)
  )`);
});

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

fastify.post('/add_to_cart', async (request, reply) => {
  const { cart_id, item_id, count } = request.body;

  if (!cart_id || !Number.isInteger(item_id) || !Number.isInteger(count) || count <= 0) {
    return reply.status(400).send({ error: 'Invalid request' });
  }

  db.get(`SELECT * FROM carts WHERE cart_id = ?`, [cart_id], (err, row) => {
    if (err || !row) {
      return reply.status(404).send({ error: 'Cart not found' });
    }

    db.get(`SELECT * FROM cart_items WHERE cart_id = ? AND item_id = ?`, [cart_id, item_id], (err, itemRow) => {
      if (err) {
        return reply.status(500).send({ error: 'Database error' });
      }

      if (itemRow) {
        const newCount = itemRow.count + count;
        db.run(`UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?`, [newCount, cart_id, item_id], (err) => {
          if (err) {
            return reply.status(500).send({ error: 'Failed to update cart' });
          }
          reply.status(200).send({ message: 'Item updated successfully' });
        });
      } else {
        db.run(`INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)`, [cart_id, item_id, count], (err) => {
          if (err) {
            return reply.status(500).send({ error: 'Failed to add item to cart' });
          }
          reply.status(200).send({ message: 'Item added successfully' });
        });
      }
    });
  });
});

fastify.post('/retrieve_cart', async (request, reply) => {
  const { cart_id } = request.body;

  if (!cart_id) {
    return reply.status(400).send({ error: 'Invalid request' });
  }

  db.get(`SELECT * FROM carts WHERE cart_id = ?`, [cart_id], (err, row) => {
    if (err || !row) {
      return reply.status(404).send({ error: 'Cart not found' });
    }

    db.all(`SELECT item_id, count FROM cart_items WHERE cart_id = ?`, [cart_id], (err, items) => {
      if (err) {
        return reply.status(500).send({ error: 'Database error' });
      }
      reply.status(200).send({ items });
    });
  });
});

fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});