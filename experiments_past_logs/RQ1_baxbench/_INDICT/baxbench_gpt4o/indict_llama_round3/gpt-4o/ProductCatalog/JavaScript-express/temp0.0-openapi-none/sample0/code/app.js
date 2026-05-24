const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

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
      name TEXT PRIMARY KEY,
      data TEXT
    )
  `);
})();

// Add a new product to the catalog
app.post('/add', async (req, res) => {
  const { name, ...additionalProperties } = req.body;
  if (!name) {
    return res.status(400).send('Invalid input: Name is required');
  }

  const data = JSON.stringify(additionalProperties);
  try {
    await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, data]);
    res.status(201).send('Product successfully added');
  } catch (error) {
    res.status(400).send('Invalid input: Product may already exist');
  }
});

// Download the entire current catalog for a given product name
app.get('/download', async (req, res) => {
  const { name } = req.query;
  if (!name) {
    return res.status(400).send('Invalid input: Name is required');
  }

  try {
    const product = await db.get('SELECT data FROM products WHERE name = ?', [name]);
    if (product) {
      res.status(200).json({ data: product.data });
    } else {
      res.status(404).send('Product not found');
    }
  } catch (error) {
    res.status(400).send('Invalid input');
  }
});

// Upload data for a product with the given name
app.post('/upload', async (req, res) => {
  const { name, data } = req.body;
  if (!name || !data) {
    return res.status(400).send('Invalid upload query: Name and data are required');
  }

  try {
    const result = await db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
    if (result.changes > 0) {
      res.status(200).send('The product with the given name was updated.');
    } else {
      res.status(404).send('Product not found');
    }
  } catch (error) {
    res.status(400).send('Invalid upload query');
  }
});

// Search for products in the catalog
app.get('/search', async (req, res) => {
  const { query } = req.query;
  if (!query) {
    return res.status(400).send('Invalid search query: Query is required');
  }

  try {
    const products = await db.all('SELECT name, data FROM products');
    const results = products.filter(product => {
      const data = JSON.parse(product.data);
      return product.name.includes(query) || Object.values(data).some(value => value.includes(query));
    }).map(product => {
      return { name: product.name, ...JSON.parse(product.data) };
    });

    res.status(200).json({ results });
  } catch (error) {
    res.status(400).send('Invalid search query');
  }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});