const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');

dotenv.config();

const dbPromise = open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
});

// Initialize the database
async function initDb() {
    const db = await dbPromise;
    await db.exec(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    `);
    await db.exec(`
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            secret TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        );
    `);
}

// User registration
fastify.post('/register', async (request, reply) => {
    const { email, username, password } = request.body;

    if (!email || !username || !password) {
        return reply.status(400).send({ message: 'Email, username, and password are required.' });
    }

    const db = await dbPromise;
    const hashedPassword = await bcrypt.hash(password, 10);

    try {
        await db.run('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', [email, username, hashedPassword]);
        return reply.status(201).send({ message: 'Registration successful' });
    } catch (error) {
        if (error.code === 'SQLITE_CONSTRAINT') {
            return reply.status(400).send({ message: 'Email already in use or invalid data' });
        }
        return reply.status(500).send({ message: 'Internal server error' });
    }
});

// User login
fastify.post('/login', async (request, reply) => {
    const { email, password } = request.body;

    if (!email || !password) {
        return reply.status(400).send({ message: 'Email and password are required.' });
    }

    const db = await dbPromise;
    const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);

    if (!user || !(await bcrypt.compare(password, user.password))) {
        return reply.status(401).send({ message: 'Invalid email or password' });
    }

    // Normally, you would return a token here, but we are not implementing authentication.
    return reply.status(200).send({ message: 'Login successful' });
});

// Set secret
fastify.post('/set_secret', async (request, reply) => {
    const { username, secret } = request.body;

    if (!username || !secret) {
        return reply.status(400).send({ message: 'Username and secret are required.' });
    }

    const db = await dbPromise;

    try {
        await db.run('INSERT INTO secrets (username, secret) VALUES (?, ?)', [username, secret]);
        return reply.status(200).send({ message: 'Secret has been set successfully' });
    } catch (error) {
        return reply.status(500).send({ message: 'Internal server error' });
    }
});

// Get secret
fastify.get('/get_secret', async (request, reply) => {
    const { username } = request.query;

    if (!username) {
        return reply.status(400).send({ message: 'Username is required.' });
    }

    const db = await dbPromise;
    const secret = await db.get('SELECT secret FROM secrets WHERE username = ?', [username]);

    if (!secret) {
        return reply.status(404).send({ message: 'Secret not found' });
    }

    return reply.status(200).send({ secret: secret.secret });
});

// Start the server
const start = async () => {
    await initDb();
    try {
        await fastify.listen({ port: 5000, host: '0.0.0.0' });
        fastify.log.info(`Server listening on http://0.0.0.0:5000`);
    } catch (err) {
        fastify.log.error(err);
        process.exit(1);
    }
};

start();