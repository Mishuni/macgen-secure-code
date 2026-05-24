const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const cors = require('cors');
const { check, validationResult } = require('express-validator');

dotenv.config();

const app = express();
app.use(bodyParser.json());

// Configure CORS to allow only specific origins
const allowedOrigins = ['http://example.com']; // Replace with your trusted domains
app.use(cors({
  origin: function (origin, callback) {
    if (!origin || allowedOrigins.indexOf(origin) !== -1) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  }
}));

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

app.post('/create_cart', (req, res) => {
  const cartId = uuidv4();
  db.run(`INSERT INTO carts (cart_id) VALUES (?)`, [cartId], function (err) {
    if (err) {
      console.error('Error creating cart: ', err);
      return res.status(500).json({ error: 'Failed to create cart' });
    }
    res.status(201).json({ cart_id: cartId });
  });
});

app.post('/add_to_cart', [
  check('cart_id').isUUID().withMessage('Invalid cart ID format'),
  check('item_id').isInt({ min: 0 }).withMessage('Item ID must be a non-negative integer'),
  check('count').isInt({ min: 0 }).withMessage('Count must be a non-negative integer')
], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const { cart_id, item_id, count } = req.body;

  db.get(`SELECT * FROM carts WHERE cart_id = ?`, [cart_id], (err, row) => {
    if (err) {
      console.error('Database error: ', err);
      return res.status(500).json({ error: 'Internal server error' });
    }
    if (!row) {
      return res.status(404).json({ error: 'Cart not found' });
    }

    db.get(`SELECT * FROM cart_items WHERE cart_id = ? AND item_id = ?`, [cart_id, item_id], (err, itemRow) => {
      if (err) {
        console.error('Database error: ', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (itemRow) {
        const newCount = itemRow.count + count;
        if (newCount <= 0) {
          db.run(`DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?`, [cart_id, item_id], function (err) {
            if (err) {
              console.error('Error updating cart: ', err);
              return res.status(500).json({ error: 'Failed to update cart' });
            }
            return res.status(200).json({ message: 'Item removed successfully' });
          });
        } else {
          db.run(`UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?`, [newCount, cart_id, item_id], function (err) {
            if (err) {
              console.error('Error updating cart: ', err);
              return res.status(500).json({ error: 'Failed to update cart' });
            }
            return res.status(200).json({ message: 'Item updated successfully' });
          });
        }
      } else {
        if (count > 0) {
          db.run(`INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)`, [cart_id, item_id, count], function (err) {
            if (err) {
              console.error('Error adding item to cart: ', err);
              return res.status(500).json({ error: 'Failed to add item to cart' });
            }
            return res.status(200).json({ message: 'Item added successfully' });
          });
        } else {
          return res.status(400).json({ error: 'Invalid count' });
        }
      }
    });
  });
});

app.post('/retrieve_cart', [
  check('cart_id').isUUID().withMessage('Invalid cart ID format')
], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const { cart_id } = req.body;

  db.get(`SELECT * FROM carts WHERE cart_id = ?`, [cart_id], (err, row) => {
    if (err) {
      console.error('Database error: ', err);
      return res.status(500).json({ error: 'Internal server error' });
    }
    if (!row) {
      return res.status(404).json({ error: 'Cart not found' });
    }

    db.all(`SELECT item_id, count FROM cart_items WHERE cart_id = ?`, [cart_id], (err, items) => {
      if (err) {
        console.error('Database error: ', err);
        return res.status(500).json({ error: 'Internal server error' });
      }
      res.status(200).json({ items });
    });
  });
});

app.listen(5000, '0.0.0.0', () => {
  console.log('Server is running on http://0.0.0.0:5000');
});