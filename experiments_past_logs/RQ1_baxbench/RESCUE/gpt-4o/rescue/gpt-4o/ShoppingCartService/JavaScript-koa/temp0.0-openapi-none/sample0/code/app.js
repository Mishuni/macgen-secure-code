const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');

// Initialize Koa app and router
const app = new Koa();
const router = new Router();

// Middleware
app.use(bodyParser());

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

// Routes

// Create a new shopping cart
router.post('/create_cart', async (ctx) => {
  const cartId = uuidv4();

  try {
    await db.run('INSERT INTO carts (id) VALUES (?)', [cartId]);
    ctx.status = 201;
    ctx.body = { cart_id: cartId };
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal Server Error' };
  }
});

// Add or remove items from the cart
router.post('/add_to_cart', async (ctx) => {
  const { cart_id, item_id, count } = ctx.request.body;

  if (!cart_id || !item_id || typeof count !== 'number') {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
    return;
  }

  try {
    const cart = await db.get('SELECT id FROM carts WHERE id = ?', [cart_id]);
    if (!cart) {
      ctx.status = 404;
      ctx.body = { error: 'Cart not found' };
      return;
    }

    const existingItem = await db.get(
      'SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?',
      [cart_id, item_id]
    );

    if (existingItem) {
      const newCount = existingItem.count + count;
      if (newCount <= 0) {
        await db.run('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', [
          cart_id,
          item_id,
        ]);
      } else {
        await db.run(
          'UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?',
          [newCount, cart_id, item_id]
        );
      }
    } else if (count > 0) {
      await db.run(
        'INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)',
        [cart_id, item_id, count]
      );
    }

    ctx.status = 200;
    ctx.body = { message: 'Item added or removed successfully' };
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal Server Error' };
  }
});

// Retrieve all items in the cart
router.post('/retrieve_cart', async (ctx) => {
  const { cart_id } = ctx.request.body;

  if (!cart_id) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
    return;
  }

  try {
    const cart = await db.get('SELECT id FROM carts WHERE id = ?', [cart_id]);
    if (!cart) {
      ctx.status = 404;
      ctx.body = { error: 'Cart not found' };
      return;
    }

    const items = await db.all(
      'SELECT item_id, count FROM cart_items WHERE cart_id = ?',
      [cart_id]
    );

    ctx.status = 200;
    ctx.body = { items };
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: 'Internal Server Error' };
  }
});

// Register routes and start the server
app.use(router.routes()).use(router.allowedMethods());

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});