const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

// Initialize the database
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS carts (
    cart_id TEXT PRIMARY KEY
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS cart_items (
    cart_id TEXT,
    item_id INTEGER,
    count INTEGER,
    PRIMARY KEY (cart_id, item_id),
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
  )`);
});

// Middleware
app.use(bodyParser());

// Routes
router.post('/create_cart', async (ctx) => {
  const cartId = uuidv4();
  db.run(`INSERT INTO carts (cart_id) VALUES (?)`, [cartId], function(err) {
    if (err) {
      ctx.status = 500;
      ctx.body = { error: 'Failed to create cart' };
    } else {
      ctx.status = 201;
      ctx.body = { cart_id: cartId };
    }
  });
});

router.post('/add_to_cart', async (ctx) => {
  const { cart_id, item_id, count } = ctx.request.body;

  if (!cart_id || !item_id || typeof count !== 'number') {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
    return;
  }

  db.get(`SELECT * FROM carts WHERE cart_id = ?`, [cart_id], (err, row) => {
    if (err || !row) {
      ctx.status = 404;
      ctx.body = { error: 'Cart not found' };
    } else {
      db.get(`SELECT * FROM cart_items WHERE cart_id = ? AND item_id = ?`, [cart_id, item_id], (err, itemRow) => {
        if (err) {
          ctx.status = 500;
          ctx.body = { error: 'Database error' };
        } else if (itemRow) {
          const newCount = itemRow.count + count;
          if (newCount <= 0) {
            db.run(`DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?`, [cart_id, item_id], function(err) {
              if (err) {
                ctx.status = 500;
                ctx.body = { error: 'Failed to update cart' };
              } else {
                ctx.status = 200;
                ctx.body = { message: 'Item removed successfully' };
              }
            });
          } else {
            db.run(`UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?`, [newCount, cart_id, item_id], function(err) {
              if (err) {
                ctx.status = 500;
                ctx.body = { error: 'Failed to update cart' };
              } else {
                ctx.status = 200;
                ctx.body = { message: 'Item updated successfully' };
              }
            });
          }
        } else if (count > 0) {
          db.run(`INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)`, [cart_id, item_id, count], function(err) {
            if (err) {
              ctx.status = 500;
              ctx.body = { error: 'Failed to add item to cart' };
            } else {
              ctx.status = 200;
              ctx.body = { message: 'Item added successfully' };
            }
          });
        } else {
          ctx.status = 400;
          ctx.body = { error: 'Invalid count' };
        }
      });
    }
  });
});

router.post('/retrieve_cart', async (ctx) => {
  const { cart_id } = ctx.request.body;

  if (!cart_id) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid request' };
    return;
  }

  db.get(`SELECT * FROM carts WHERE cart_id = ?`, [cart_id], (err, row) => {
    if (err || !row) {
      ctx.status = 404;
      ctx.body = { error: 'Cart not found' };
    } else {
      db.all(`SELECT item_id, count FROM cart_items WHERE cart_id = ?`, [cart_id], (err, items) => {
        if (err) {
          ctx.status = 500;
          ctx.body = { error: 'Database error' };
        } else {
          ctx.status = 200;
          ctx.body = { items: items };
        }
      });
    }
  });
});

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});