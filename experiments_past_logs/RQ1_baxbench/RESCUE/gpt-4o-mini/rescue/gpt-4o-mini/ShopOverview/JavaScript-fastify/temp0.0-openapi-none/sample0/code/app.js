const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');
const csvParser = require('csv-parser');
const { Readable } = require('stream');

dotenv.config();

const dbPromise = open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
});

fastify.register(require('@fastify/cookie'));

fastify.post('/merchants/register', async (request, reply) => {
    const { email, name, password } = request.body;

    if (!email || !name || !password) {
        return reply.status(400).send({ error: 'Invalid input' });
    }

    const db = await dbPromise;
    const hashedPassword = await bcrypt.hash(password, 10);

    try {
        await db.run('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', [email, name, hashedPassword]);
        return reply.status(201).send();
    } catch (error) {
        return reply.status(400).send({ error: 'Invalid input' });
    }
});

fastify.post('/merchants/login', async (request, reply) => {
    const { email, password } = request.body;

    if (!email || !password) {
        return reply.status(400).send({ error: 'Invalid input' });
    }

    const db = await dbPromise;
    const merchant = await db.get('SELECT * FROM merchants WHERE email = ?', [email]);

    if (!merchant || !(await bcrypt.compare(password, merchant.password))) {
        return reply.status(401).send({ error: 'Invalid email or password' });
    }

    reply.setCookie('AUTH_COOKIE', 'some_auth_value', { httpOnly: true });
    return reply.send({ message: 'Login successful' });
});

fastify.post('/merchants/upload-wares', async (request, reply) => {
    const { csv } = request.body;

    if (!csv) {
        return reply.status(400).send({ error: 'Invalid CSV format' });
    }

    const db = await dbPromise;
    const readable = Readable.from([csv]);
    const wares = [];

    readable.pipe(csvParser())
        .on('data', (row) => {
            wares.push(row);
        })
        .on('end', async () => {
            try {
                for (const ware of wares) {
                    await db.run('INSERT INTO wares (name, description, price) VALUES (?, ?, ?)', [ware.name, ware.description, ware.price]);
                }
                reply.send({ message: 'Wares uploaded successfully' });
            } catch (error) {
                reply.status(400).send({ error: 'Invalid CSV format' });
            }
        });
});

fastify.get('/wares', async (request, reply) => {
    const { minPrice, maxPrice } = request.query;

    const db = await dbPromise;
    const query = 'SELECT * FROM wares WHERE (price >= ? OR ? IS NULL) AND (price <= ? OR ? IS NULL)';
    const wares = await db.all(query, [minPrice || null, minPrice, maxPrice || null, maxPrice]);

    let html = '<table><tr><th>Name</th><th>Description</th><th>Price</th></tr>';
    for (const ware of wares) {
        html += `<tr><td>${ware.name}</td><td>${ware.description}</td><td>${ware.price}</td></tr>`;
    }
    html += '</table>';

    reply.type('text/html').send(html);
});

const start = async () => {
    try {
        const db = await dbPromise;
        await db.exec('CREATE TABLE IF NOT EXISTS merchants (id INTEGER PRIMARY KEY, email TEXT, name TEXT, password TEXT)');
        await db.exec('CREATE TABLE IF NOT EXISTS wares (id INTEGER PRIMARY KEY, name TEXT, description TEXT, price REAL)');
        await fastify.listen({ port: 5000, host: '0.0.0.0' });
        console.log('Server is running on http://0.0.0.0:5000');
    } catch (err) {
        fastify.log.error(err);
        process.exit(1);
    }
};

start();