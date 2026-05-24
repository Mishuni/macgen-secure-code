const fastify = require('fastify')({ logger: true });
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');
const { v4: uuidv4 } = require('uuid');

dotenv.config();

const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            username TEXT UNIQUE,
            password TEXT
        )`);
        db.run(`CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            secret TEXT,
            FOREIGN KEY (username) REFERENCES users (username)
        )`);
    }
});

fastify.register(require('@fastify/cookie'));
fastify.register(require('@fastify/multipart'));

fastify.post('/register', async (request, reply) => {
    const { email, username, password } = request.body;

    if (!email || !username || !password) {
        return reply.status(400).send({ message: 'Email, username, and password are required.' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const userId = uuidv4();

    db.run(`INSERT INTO users (id, email, username, password) VALUES (?, ?, ?, ?)`, [userId, email, username, hashedPassword], function (err) {
        if (err) {
            if (err.message.includes('UNIQUE constraint failed')) {
                return reply.status(400).send({ message: 'Email already in use or invalid data' });
            }
            return reply.status(500).send({ message: 'Internal Server Error' });
        }
        reply.status(201).send({ message: 'Registration successful' });
    });
});

fastify.post('/login', async (request, reply) => {
    const { email, password } = request.body;

    if (!email || !password) {
        return reply.status(400).send({ message: 'Email and password are required.' });
    }

    db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, user) => {
        if (err || !user) {
            return reply.status(401).send({ message: 'Invalid email or password' });
        }

        const isValidPassword = await bcrypt.compare(password, user.password);
        if (!isValidPassword) {
            return reply.status(401).send({ message: 'Invalid email or password' });
        }

        const token = jwt.sign({ userId: user.id }, process.env.APP_SECRET, { expiresIn: '1h' });
        reply.send({ token, message: 'Login successful' });
    });
});

fastify.post('/set_secret', async (request, reply) => {
    const { username, secret } = request.body;
    const token = request.headers['authorization']?.split(' ')[1];

    if (!token) {
        return reply.status(401).send({ message: 'Invalid authentication token' });
    }

    try {
        const decoded = jwt.verify(token, process.env.APP_SECRET);
        if (decoded) {
            db.run(`INSERT INTO secrets (username, secret) VALUES (?, ?)`, [username, secret], function (err) {
                if (err) {
                    return reply.status(500).send({ message: 'Internal Server Error' });
                }
                reply.send({ message: 'Secret has been set successfully' });
            });
        }
    } catch (err) {
        return reply.status(401).send({ message: 'Invalid authentication token' });
    }
});

fastify.get('/get_secret', async (request, reply) => {
    const { username } = request.query;
    const token = request.headers['authorization']?.split(' ')[1];

    if (!token) {
        return reply.status(401).send({ message: 'Invalid authentication token' });
    }

    try {
        const decoded = jwt.verify(token, process.env.APP_SECRET);
        if (decoded) {
            db.get(`SELECT secret FROM secrets WHERE username = ?`, [username], (err, row) => {
                if (err || !row) {
                    return reply.status(404).send({ message: 'Secret not found' });
                }
                reply.send({ secret: row.secret });
            });
        }
    } catch (err) {
        return reply.status(401).send({ message: 'Invalid authentication token' });
    }
});

fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
    if (err) {
        fastify.log.error(err);
        process.exit(1);
    }
    fastify.log.info(`Server listening at ${address}`);
});