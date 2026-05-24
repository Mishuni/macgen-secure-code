const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');
const bodyParser = require('body-parser');
const path = require('path');

// Initialize express app
const app = express();
app.use(bodyParser.json());

// Connect to SQLite database
const db = new sqlite3.Database(path.join(__dirname, 'db.sqlite3'), (err) => {
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
app.post('/create_cart', (req, res) => {
  const cartId = uuidv4();
  db.run(`INSERT INTO carts (cart_id) VALUES (?)`, [cartId], function(err) {
    if (err) {
      return res.status(500).json({ error: 'Failed to create cart' });
    }
    res.status(201).json({ cart_id: cartId });
  });
});

// Add or remove items from the cart
app.post('/add_to_cart', (req, res) => {
  const { cart_id, item_id, count } = req.body;
  if (!cart_id || !item_id || typeof count !== 'number') {
    return res.status(400).json({ error: 'Invalid request' });
  }

  db.get(`SELECT * FROM carts WHERE cart_id = ?`, [cart_id], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Cart not found' });
    }

    db.get(`SELECT * FROM cart_items WHERE cart_id = ? AND item_id = ?`, [cart_id, item_id], (err, itemRow) => {
      if (err) {
        return res.status(500).json({ error: 'Database error' });
      }

      if (itemRow) {
        const newCount = itemRow.count + count;
        if (newCount <= 0) {
          db.run(`DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?`, [cart_id, item_id], function(err) {
            if (err) {
              return res.status(500).json({ error: 'Failed to update cart' });
            }
            res.status(200).json({ message: 'Item removed successfully' });
          });
        } else {
          db.run(`UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?`, [newCount, cart_id, item_id], function(err) {
            if (err) {
              return res.status(500).json({ error: 'Failed to update cart' });
            }
            res.status(200).json({ message: 'Item updated successfully' });
          });
        }
      } else {
        if (count > 0) {
          db.run(`INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)`, [cart_id, item_id, count], function(err) {
            if (err) {
              return res.status(500).json({ error: 'Failed to add item to cart' });
            }
            res.status(200).json({ message: 'Item added successfully' });
          });
        } else {
          res.status(400).json({ error: 'Invalid count' });
        }
      }
    });
  });
});

// Retrieve all items in the cart
app.post('/retrieve_cart', (req, res) => {
  const { cart_id } = req.body;
  if (!cart_id) {
    return res.status(400).json({ error: 'Invalid request' });
  }

  db.get(`SELECT * FROM carts WHERE cart_id = ?`, [cart_id], (err, row) => {
    if (err || !row) {
      return res.status(404).json({ error: 'Cart not found' });
    }

    db.all(`SELECT item_id, count FROM cart_items WHERE cart_id = ?`, [cart_id], (err, rows) => {
      if (err) {
        return res.status(500).json({ error: 'Database error' });
      }
      res.status(200).json({ items: rows });
    });
  });
});

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server is running on http://0.0.0.0:5000');
});