import fastify from 'fastify';
import { open } from 'sqlite';
import sqlite3 from 'sqlite3';
import dotenv from 'dotenv';

dotenv.config();

const app = fastify();
const dbFile = 'db.sqlite3';

// Initialize SQLite database
async function initDatabase() {
    const db = await open({
        filename: dbFile,
        driver: sqlite3.Database
    });

    await db.exec(`
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            data TEXT NOT NULL
        )
    `);

    return db;
}

// Add a new product
app.post('/add', async (request, reply) => {
    const { name, ...additionalProperties } = request.body;

    if (!name || typeof name !== 'string') {
        return reply.status(400).send({ error: 'Invalid input' });
    }

    const db = await initDatabase();
    const data = JSON.stringify(additionalProperties);

    try {
        await db.run('INSERT INTO products (name, data) VALUES (?, ?)', [name, data]);
        reply.status(201).send({ message: 'Product successfully added' });
    } catch (error) {
        if (error.code === 'SQLITE_CONSTRAINT') {
            return reply.status(400).send({ error: 'Product already exists' });
        }
        reply.status(500).send({ error: 'Database error' });
    }
});

// Download product data
app.get('/download', async (request, reply) => {
    const { name } = request.query;

    if (!name || typeof name !== 'string') {
        return reply.status(400).send({ error: 'Invalid input' });
    }

    const db = await initDatabase();
    const product = await db.get('SELECT * FROM products WHERE name = ?', [name]);

    if (!product) {
        return reply.status(404).send({ error: 'Product not found' });
    }

    reply.send({ data: product.data });
});

// Upload product data
app.post('/upload', async (request, reply) => {
    const { name, data } = request.body;

    if (!name || typeof name !== 'string' || !data || typeof data !== 'string') {
        return reply.status(400).send({ error: 'Invalid upload query' });
    }

    const db = await initDatabase();

    try {
        await db.run('INSERT OR REPLACE INTO products (name, data) VALUES (?, ?)', [name, data]);
        reply.send({ message: 'Product updated successfully' });
    } catch (error) {
        reply.status(500).send({ error: 'Database error' });
    }
});

// Search for products
app.get('/search', async (request, reply) => {
    const { query } = request.query;

    if (!query || typeof query !== 'string') {
        return reply.status(400).send({ error: 'Invalid search query' });
    }

    const db = await initDatabase();
    const products = await db.all('SELECT * FROM products WHERE name LIKE ? OR data LIKE ?', [`%${query}%`, `%${query}%`]);

    reply.send({ results: products });
});

// Start the server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
    if (err) {
        console.error(err);
        process.exit(1);
    }
    console.log(`Server listening at ${address}`);
});