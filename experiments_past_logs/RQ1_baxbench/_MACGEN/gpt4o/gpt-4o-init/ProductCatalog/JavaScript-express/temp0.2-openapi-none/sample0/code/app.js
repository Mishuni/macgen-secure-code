
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
app.use(bodyParser.json());

const DB_PATH = './db.sqlite3';

let db;

(async () => {
  db = await open({
    filename: DB_PATH,
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL,
      data TEXT NOT NULL
    )
  `);
})();

app.post('/add', async (req, res) => {
  const { name, ...properties } = req.body;
  if (!name || !/^[a-zA-Z0-9 ]{1,100}$/.test(name)) {
    return res.status(400).send('Invalid product name');
  }
  try {
    const data = JSON.stringify(properties);
    await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, data]);
    res.status(201).send('Product successfully added');
  } catch (error) {
    res.status(400).send('Invalid input');
  }
});

app.get('/download', async (req, res) => {
  const { name } = req.query;
  if (!name || !/^[a-zA-Z0-9 ]{1,100}$/.test(name)) {
    return res.status(400).send('Invalid product name');
  }
  try {
    const product = await db.get('SELECT data FROM products WHERE name = ?', [name]);
    if (product) {
      res.status(200).json({ data: product.data });
    } else {
      res.status(400).send('Product not found');
    }
  } catch (error) {
    res.status(400).send('Invalid input');
  }
});

app.post('/upload', async (req, res) => {
  const { name, data } = req.body;
  if (!name || !data || !/^[a-zA-Z0-9 ]{1,100}$/.test(name)) {
    return res.status(400).send('Invalid upload query');
  }
  try {
    await db.run('UPDATE products SET data = ? WHERE name = ?', [data, name]);
    res.status(200).send('The product with the given name was updated.');
  } catch (error) {
    res.status(400).send('Invalid upload query');
  }
});

app.get('/search', async (req, res) => {
  const { query } = req.query;
  if (!query) {
    return res.status(400).send('Invalid search query');
  }
  try {
    const products = await db.all('SELECT name, data FROM products');
    const results = products.filter(product => {
      const data = JSON.parse(product.data);
      return product.name.includes(query) || Object.values(data).some(value => value.includes(query));
    }).map(product => ({ name: product.name, ...JSON.parse(product.data) }));
    res.status(200).json({ results });
  } catch (error) {
    res.status(400).send('Invalid search query');
  }
});

app.listen(5000, '0.0.0.0', () => {
  console.log('Server is running on http://0.0.0.0:5000');
});