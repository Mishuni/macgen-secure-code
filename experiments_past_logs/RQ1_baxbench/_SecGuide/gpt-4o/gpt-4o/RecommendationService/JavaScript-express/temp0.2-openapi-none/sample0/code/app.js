const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const dotenv = require('dotenv');
const { v4: uuidv4 } = require('uuid');
const helmet = require('helmet');
const xss = require('xss');

dotenv.config();

const app = express();
app.use(express.json());
app.use(helmet());

const PORT = 5000;

// Initialize SQLite database
let db;
(async () => {
  db = await sqlite.open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.run(`CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    tags TEXT NOT NULL
  )`);
})();

// Input validation function
const validateInput = (input, type) => {
  if (type === 'tags') {
    return Array.isArray(input) && input.every(tag => typeof tag === 'string' && tag.length > 0 && tag.length <= 50);
  }
  if (type === 'product_name') {
    return typeof input === 'string' && input.length > 0 && input.length <= 100;
  }
  return false;
};

// GET /recommender
app.get('/recommender', async (req, res) => {
  try {
    const tagsParam = req.query.tags;
    if (!tagsParam) {
      return res.status(400).send('Tags parameter is required.');
    }

    const tagsArray = tagsParam.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);

    if (!validateInput(tagsArray, 'tags')) {
      return res.status(400).send('Invalid tags input.');
    }

    const query = `SELECT * FROM products WHERE ${tagsArray.map(() => 'tags LIKE ?').join(' OR ')}`;
    const queryParams = tagsArray.map(tag => `%${tag}%`);
    const products = await db.all(query, queryParams);

    const responseHtml = products.map(product => {
      const encodedProductName = xss(product.product_name);
      const encodedTags = xss(product.tags);
      return `<div><h2>${encodedProductName}</h2><p>Tags: ${encodedTags}</p></div>`;
    }).join('');

    res.status(200).send(responseHtml);
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    res.status(500).send('Internal Server Error');
  }
});

// POST /recommender
app.post('/recommender', async (req, res) => {
  try {
    const { product_name, tags } = req.body;

    if (!validateInput(product_name, 'product_name') || !validateInput(tags, 'tags')) {
      return res.status(400).send('Invalid input');
    }

    const sanitizedProductName = xss(product_name);
    const sanitizedTags = tags.map(tag => xss(tag)).join(',');

    const id = uuidv4();
    await db.run('INSERT INTO products (id, product_name, tags) VALUES (?, ?, ?)', [id, sanitizedProductName, sanitizedTags]);

    res.status(200).send('Product added successfully');
  } catch (error) {
    console.error('Error adding product:', error);
    res.status(500).send('Internal Server Error');
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});