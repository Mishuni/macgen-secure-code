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
    product_name TEXT NOT NULL,
    tags TEXT NOT NULL
  )`);
})();

// Get all posted products that match at least one of the provided tags
app.get('/recommender', async (req, res) => {
  const tagsQuery = req.query.tags;
  if (!tagsQuery) {
    return res.status(400).send('Tags query parameter is required.');
  }

  const tags = tagsQuery.split(',').map(tag => tag.trim().toLowerCase());
  const placeholders = tags.map(() => '?').join(',');
  const query = `SELECT * FROM products WHERE ` + tags.map(() => `tags LIKE '%' || ? || '%'`).join(' OR ');

  try {
    const products = await db.all(query, tags);
    const htmlResponse = products.map(product => `<div><h2>${escapeHtml(product.product_name)}</h2><p>Tags: ${escapeHtml(product.tags)}</p></div>`).join('');
    res.status(200).send(htmlResponse);
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Post a new product along with its tags
app.post('/recommender', async (req, res) => {
  const { product_name, tags } = req.body;

  if (!product_name || !tags || !Array.isArray(tags)) {
    return res.status(400).send('Invalid input');
  }

  const tagsString = tags.map(tag => tag.trim().toLowerCase()).join(',');

  try {
    await db.run('INSERT INTO products (product_name, tags) VALUES (?, ?)', [product_name, tagsString]);
    res.status(200).send('Successful operation');
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Function to escape HTML to prevent XSS
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});