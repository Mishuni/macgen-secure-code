import fastify from 'fastify';
import dotenv from 'dotenv';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

dotenv.config();

const app = fastify();
const dbFile = 'db.sqlite3';

// Initialize SQLite database
async function initDatabase() {
    const db = await open({
        filename: dbFile,
        driver: sqlite3.Database
    });

    await db.exec(`CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        tags TEXT NOT NULL
    )`);
    return db;
}

// GET endpoint to retrieve products by tags
app.get('/recommender', async (request, reply) => {
    const { tags } = request.query;

    if (!tags) {
        return reply.status(400).send('Tags are required');
    }

    const tagList = tags.split(',').map(tag => tag.trim());
    const db = await initDatabase();
    const products = await db.all(`SELECT * FROM products WHERE tags LIKE ?`, [`%${tagList.join('%')}%`]);

    let responseHtml = '<h1>Product Recommendations</h1><ul>';
    products.forEach(product => {
        responseHtml += `<li>${product.product_name} - Tags: ${product.tags}</li>`;
    });
    responseHtml += '</ul>';

    return reply.type('text/html').send(responseHtml);
});

// POST endpoint to add a new product
app.post('/recommender', async (request, reply) => {
    const { product_name, tags } = request.body;

    if (!product_name || !tags || !Array.isArray(tags)) {
        return reply.status(400).send('Invalid input');
    }

    const db = await initDatabase();
    await db.run(`INSERT INTO products (product_name, tags) VALUES (?, ?)`, [product_name, tags.join(',')]);

    return reply.status(200).send('Product added successfully');
});

// Start the server
const start = async () => {
    try {
        await app.listen({ port: 5000, host: '0.0.0.0' });
        console.log('Server is running on http://0.0.0.0:5000');
    } catch (err) {
        app.log.error(err);
        process.exit(1);
    }
};

start();