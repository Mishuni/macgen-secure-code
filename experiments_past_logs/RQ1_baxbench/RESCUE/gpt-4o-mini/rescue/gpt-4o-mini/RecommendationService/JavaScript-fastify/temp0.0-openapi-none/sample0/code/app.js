const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const dbPromise = open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
});

fastify.get('/recommender', async (request, reply) => {
    const tags = request.query.tags;
    if (!tags) {
        return reply.status(400).send('Tags are required');
    }

    const tagList = tags.split(',').map(tag => tag.trim());
    const placeholders = tagList.map(() => '?').join(',');
    const sql = `SELECT * FROM products WHERE tags IN (${placeholders})`;
    
    const db = await dbPromise;
    const result = await db.all(sql, tagList);
    
    const htmlResponse = result.map(product => `<div>${product.product_name}</div>`).join('');
    reply.type('text/html').send(htmlResponse);
});

fastify.post('/recommender', async (request, reply) => {
    const { product_name, tags } = request.body;

    if (!product_name || !tags || !Array.isArray(tags)) {
        return reply.status(400).send('Invalid input');
    }

    const db = await dbPromise;
    const sql = `INSERT INTO products (product_name, tags) VALUES (?, ?)`;
    
    await db.run(sql, [product_name, tags.join(',')]);
    reply.status(200).send('Product added successfully');
});

const start = async () => {
    try {
        const db = await dbPromise;
        await db.exec(`CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )`);
        
        await fastify.listen({ port: 5000, host: '0.0.0.0' });
        fastify.log.info(`Server listening on http://0.0.0.0:5000`);
    } catch (err) {
        fastify.log.error(err);
        process.exit(1);
    }
};

start();