const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const bodyParser = require('body-parser');
const helmet = require('helmet');
const cors = require('cors');
const Joi = require('joi');

dotenv.config();

const app = express();
app.use(bodyParser.json());
app.use(helmet());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS ? process.env.ALLOWED_ORIGINS.split(',') : []
}));

const PORT = 5000;

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      data TEXT
    )
  `);
})();

// Validation schemas
const productSchema = Joi.object({
  name: Joi.string().max(255).required(),
  data: Joi.any()
});

const querySchema = Joi.object({
  query: Joi.string().max(255).required()
});

// Add a new product to the catalog
app.post('/add', async (req, res) => {
  const { error, value } = productSchema.validate(req.body);
  if (error) {
    return res.status(400).json({ error: 'Invalid input' });
  }

  const { name, ...additionalProperties } = value;

  try {
    const sanitizedData = JSON.stringify(additionalProperties);
    await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, sanitizedData]);
    res.status(201).json({ message: 'Product successfully added' });
  } catch (error) {
    res.status(400).json({ error: 'Product already exists' });
  }
});

// Download the entire current catalog for a given product name
app.get('/download', async (req, res) => {
  const { error, value } = productSchema.validate(req.query);
  if (error) {
    return res.status(400).json({ error: 'Invalid input' });
  }

  const { name } = value;

  try {
    const product = await db.get('SELECT data FROM products WHERE name = ?', [name]);
    if (product) {
      res.status(200).json({ data: product.data });
    } else {
      res.status(404).json({ error: 'Product not found' });
    }
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Upload data for a product with the given name
app.post('/upload', async (req, res) => {
  const { error, value } = productSchema.validate(req.body);
  if (error) {
    return res.status(400).json({ error: 'Invalid upload query' });
  }

  const { name, data } = value;

  try {
    const result = await db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
    if (result.changes > 0) {
      res.status(200).json({ message: 'The product with the given name was updated.' });
    } else {
      res.status(404).json({ error: 'Product not found' });
    }
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Search for products in the catalog
app.get('/search', async (req, res) => {
  const { error, value } = querySchema.validate(req.query);
  if (error) {
    return res.status(400).json({ error: 'Invalid search query' });
  }

  const { query } = value;

  try {
    const sanitizedQuery = `%${query}%`;
    const products = await db.all('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', [sanitizedQuery, sanitizedQuery]);
    const results = products.map(product => ({
      name: product.name,
      ...JSON.parse(product.data)
    }));
    res.status(200).json({ results });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});