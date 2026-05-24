const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');

dotenv.config();

const app = express();
app.use(bodyParser.json());

const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

async function initializeDatabase() {
  const db = await dbPromise;
  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      data TEXT
    )
  `);
}

app.post('/add', async (req, res) => {
  try {
    const { name, ...additionalProperties } = req.body;
    if (!name) {
      return res.status(400).json({ error: 'Product name is required' });
    }
    const db = await dbPromise;
    const id = uuidv4();
    const data = JSON.stringify(additionalProperties);
    await db.run('INSERT INTO products (id, name, data) VALUES (?, ?, ?)', [id, name, data]);
    res.status(201).json({ message: 'Product successfully added' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/download', async (req, res) => {
  try {
    const { name } = req.query;
    if (!name) {
      return res.status(400).json({ error: 'Product name is required' });
    }
    const db = await dbPromise;
    const product = await db.get('SELECT * FROM products WHERE name = ?', [name]);
    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }
    res.status(200).json({ data: product.data });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/upload', async (req, res) => {
  try {
    const { name, data } = req.body;
    if (!name || !data) {
      return res.status(400).json({ error: 'Product name and data are required' });
    }
    const db = await dbPromise;
    const result = await db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
    if (result.changes === 0) {
      return res.status(404).json({ error: 'Product not found' });
    }
    res.status(200).json({ message: 'Product successfully updated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/search', async (req, res) => {
  try {
    const { query } = req.query;
    if (!query) {
      return res.status(400).json({ error: 'Search query is required' });
    }
    const db = await dbPromise;
    const products = await db.all('SELECT * FROM products WHERE name LIKE ? OR data LIKE ?', [`%${query}%`, `%${query}%`]);
    const results = products.map(product => ({
      name: product.name,
      ...JSON.parse(product.data)
    }));
    res.status(200).json({ results });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

initializeDatabase().then(() => {
  app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
  });
});