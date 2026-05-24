const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
app.use(bodyParser.json());

const PORT = 5000;

// Initialize SQLite database
let db;
(async () => {
  db = await sqlite.open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.run(`CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL
  )`);

  await db.run(`CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    tag TEXT,
    FOREIGN KEY(product_id) REFERENCES products(id)
  )`);
})();

// Function to escape HTML
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Get all posted products that match at least one of the provided tags
app.get('/recommender', async (req, res) => {
  const tags = req.query.tags;
  if (!tags) {
    return res.status(400).send('Tags query parameter is required.');
  }

  const tagList = tags.split(',').map(tag => tag.trim());
  const placeholders = tagList.map(() => '?').join(',');
  const query = `
    SELECT DISTINCT p.product_name
    FROM products p
    JOIN tags t ON p.id = t.product_id
    WHERE t.tag IN (${placeholders})
  `;

  try {
    const products = await db.all(query, tagList);
    const productNames = products.map(product => `<li>${escapeHtml(product.product_name)}</li>`).join('');
    res.status(200).send(`<ul>${productNames}</ul>`);
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Post a new product along with its tags
app.post('/recommender', async (req, res) => {
  const { product_name, tags } = req.body;

  if (!product_name || !tags || !Array.isArray(tags) || tags.length === 0) {
    return res.status(400).send('Invalid input');
  }

  try {
    const result = await db.run('INSERT INTO products (product_name) VALUES (?)', [product_name]);
    const productId = result.lastID;

    const tagInsertPromises = tags.map(tag => {
      return db.run('INSERT INTO tags (product_id, tag) VALUES (?, ?)', [productId, tag]);
    });

    await Promise.all(tagInsertPromises);
    res.status(200).send('Successful operation');
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});