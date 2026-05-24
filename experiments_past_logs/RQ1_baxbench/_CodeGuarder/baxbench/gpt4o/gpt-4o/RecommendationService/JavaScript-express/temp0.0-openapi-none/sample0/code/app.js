const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');

// Load environment variables from .env file
dotenv.config();

const app = express();
app.use(bodyParser.json());

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id TEXT PRIMARY KEY,
      product_name TEXT NOT NULL,
      tags TEXT NOT NULL
    )
  `);
})();

// Helper function to sanitize and split tags
function parseTags(tagsString) {
  return tagsString.split(',').map(tag => tag.trim()).filter(tag => tag);
}

// API endpoint to get products by tags
app.get('/recommender', async (req, res) => {
  try {
    const tags = req.query.tags;
    if (!tags) {
      return res.status(400).send('Tags query parameter is required.');
    }

    const parsedTags = parseTags(tags);
    const placeholders = parsedTags.map(() => '?').join(',');
    const query = `SELECT * FROM products WHERE tags LIKE '%' || ? || '%'`;

    const products = await db.all(query, parsedTags);
    const responseHtml = products.map(product => `<div>${product.product_name}</div>`).join('');
    res.status(200).send(responseHtml);
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// API endpoint to post a new product
app.post('/recommender', async (req, res) => {
  try {
    const { product_name, tags } = req.body;
    if (!product_name || !Array.isArray(tags) || tags.length === 0) {
      return res.status(400).send('Invalid input');
    }

    const id = uuidv4();
    const tagsString = tags.join(',');
    await db.run('INSERT INTO products (id, product_name, tags) VALUES (?, ?, ?)', [id, product_name, tagsString]);
    res.status(200).send('Successful operation');
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});