const fastify = require('fastify')({ logger: true });
const dotenv = require('dotenv');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');
const csvParser = require('csv-parser');
const fs = require('fs');
const path = require('path');

// Load environment variables
dotenv.config();
const APP_SECRET = process.env.APP_SECRET || 'default_secret';

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS merchants (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            name TEXT,
            password TEXT
        )`);
        db.run(`CREATE TABLE IF NOT EXISTS wares (
            id TEXT PRIMARY KEY,
            merchant_id TEXT,
            name TEXT,
            description TEXT,
            price REAL,
            FOREIGN KEY (merchant_id) REFERENCES merchants(id)
        )`);
    }
});

// Middleware for cookie handling
fastify.register(require('@fastify/cookie'));

// Merchant registration
fastify.post('/merchants/register', async (request, reply) => {
    const { email, name, password } = request.body;

    if (!email || !name || !password) {
        return reply.status(400).send({ error: 'Invalid input' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const id = uuidv4();

    db.run(`INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)`, [id, email, name, hashedPassword], function(err) {
        if (err) {
            return reply.status(400).send({ error: 'Email already exists' });
        }
        reply.status(201).send({ message: 'Merchant registered successfully' });
    });
});

// Merchant login
fastify.post('/merchants/login', async (request, reply) => {
    const { email, password } = request.body;

    db.get(`SELECT * FROM merchants WHERE email = ?`, [email], async (err, row) => {
        if (err || !row || !(await bcrypt.compare(password, row.password))) {
            return reply.status(401).send({ error: 'Invalid email or password' });
        }
        reply.setCookie('AUTH_COOKIE', row.id, { path: '/', httpOnly: true });
        reply.send({ message: 'Login successful' });
    });
});

// Upload wares
fastify.post('/merchants/upload-wares', async (request, reply) => {
    const merchantId = request.cookies.AUTH_COOKIE;

    if (!merchantId) {
        return reply.status(401).send({ error: 'Unauthorized' });
    }

    const { csv } = request.body;

    const wares = [];
    fs.createReadStream(path.join(__dirname, csv))
        .pipe(csvParser())
        .on('data', (data) => {
            wares.push({ ...data, merchant_id: merchantId });
        })
        .on('end', () => {
            const stmt = db.prepare(`INSERT INTO wares (id, merchant_id, name, description, price) VALUES (?, ?, ?, ?, ?)`);
            wares.forEach(ware => {
                stmt.run(uuidv4(), ware.merchant_id, ware.name, ware.description, ware.price);
            });
            stmt.finalize();
            reply.send({ message: 'Wares uploaded successfully' });
        })
        .on('error', () => {
            reply.status(400).send({ error: 'Invalid CSV format' });
        });
});

// Retrieve wares
fastify.get('/wares', (request, reply) => {
    const { minPrice, maxPrice } = request.query;
    let query = `SELECT wares.name, wares.price, wares.description, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id`;
    const params = [];

    if (minPrice) {
        query += ' WHERE wares.price >= ?';
        params.push(minPrice);
    }
    if (maxPrice) {
        query += (params.length ? ' AND' : ' WHERE') + ' wares.price <= ?';
        params.push(maxPrice);
    }

    db.all(query, params, (err, rows) => {
        if (err) {
            return reply.status(500).send({ error: 'Database error' });
        }
        let html = '<table><tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant Email</th></tr>';
        rows.forEach(row => {
            html += `<tr><td>${row.name}</td><td>${row.price}</td><td>${row.description}</td><td>${row.email}</td></tr>`;
        });
        html += '</table>';
        reply.type('text/html').send(html);
    });
});

// Start server
fastify.listen(5000, '0.0.0.0', (err, address) => {
    if (err) {
        fastify.log.error(err);
        process.exit(1);
    }
    fastify.log.info(`Server listening at ${address}`);
});